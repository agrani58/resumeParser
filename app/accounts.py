from dotenv import load_dotenv
from streamlit import secrets
import stripe
import re
import time
import streamlit as st
from datetime import datetime as dt, timedelta, timezone
from app.config import cookie_controller
from app.schema import delete_session_token, get_connection, create_session_token, create_user, verify_user
from app.libraries import *
from app.view import display_footer
from app.payments import create_checkout_session
from app.components import main_components
import os
import secrets
from app.home import clear_user_files

load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def is_password_strong(password):
    return (len(password) >= 3 and 
            any(c in "!@#$%^&*()-_" for c in password))

def check_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    session_token = cookie_controller.get("session_token")
    if not session_token:
        st.session_state.authenticated = False
        return False

    try:
        with get_connection() as conn:
            with conn.cursor(buffered=True) as cursor:
                cursor.execute("""
                    SELECT 
                        u.email, 
                        u.username, 
                        u.role_id, 
                        u.signup_date, 
                        COALESCE(s.subscription_type, 'free') 
                    FROM user_sessions sess
                    JOIN users u ON sess.email = u.email
                    LEFT JOIN subscriptions s 
                        ON u.email = s.email AND s.is_active = TRUE
                    WHERE sess.session_token = %s 
                        AND sess.expires_at > UTC_TIMESTAMP()
                    LIMIT 1
                """, (session_token,))
                
                session = cursor.fetchone()
                if session:
                    st.session_state.update({
                        'authenticated': True,
                        'email': session[0],
                        'username': session[1],
                        'role_id': session[2],
                        'signup_date': session[3],
                        'subscription_type': session[4]
                    })
                    return True
                return False
    except Exception as e:
        st.error(f"Session error: {str(e)}")
        return False

def login(email, password):
    if not is_valid_email(email):
        st.error("Invalid email format.")
        return

    verification = verify_user(email, password)
    
    if not verification or not isinstance(verification, dict) or not verification.get('status'):
        st.error("Login failed. Check your credentials.")
        return
    
    st.session_state.role_id = verification.get('role_id')
    
    session_token = secrets.token_urlsafe(32)
    expires_at = dt.now(timezone.utc) + timedelta(days=1)
    
    if create_session_token(email, session_token, expires_at):
        cookie_controller.set("session_token", session_token, 
            max_age=int((expires_at - dt.now(timezone.utc)).total_seconds()))       
        st.session_state.update({
            'authenticated': True,
            'email': email,
            'username': verification.get('username', 'User'),
            'subscription_type': verification.get('subscription_type', 'free')
        })
        st.success("Logged in successfully!")
        time.sleep(0.5)
        st.rerun()
    else:
        st.error("Failed to create session. Please try again.")

def logout():
    clear_user_files()
    if session_token := cookie_controller.get("session_token"):
        delete_session_token(session_token)
        cookie_controller.set("session_token", "", max_age=0)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.authenticated = False
    st.rerun()

def run():
    main_components()

    payment_status = st.query_params.get("payment")
    if payment_status:
        if payment_status == "success":
            if "email" not in st.session_state:
                st.error("User email not found. Please log in again.")
                st.query_params.clear()
                return
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            UPDATE subscriptions 
                            SET is_active = FALSE 
                            WHERE email = %s
                        """, (st.session_state.email,))
                        
                        start_date = dt.now(timezone.utc)
                        end_date = start_date + timedelta(days=30)
                        
                        cursor.execute("""
                            INSERT INTO subscriptions 
                            (email, subscription_type, start_date, end_date, is_active)
                            VALUES (%s, 'premium', %s, %s, TRUE)
                        """, (st.session_state.email, start_date, end_date))
                        
                        conn.commit()
                
                st.success("✅ Payment successful! Your premium subscription is now active.")
                check_session()
                st.query_params.clear()
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Payment processing failed: {str(e)}")
                return
            
        elif payment_status == "cancel":
            st.error("❌ Payment was cancelled")
            st.query_params.clear()

    st.session_state.setdefault('authenticated', False)
    st.session_state.setdefault('form_choice', 'Login')
    check_session()

    if st.session_state.authenticated:
        st.subheader(f"Welcome {st.session_state.username}!")
        st.divider()

        try:
            with get_connection() as conn:
                with conn.cursor(buffered=True) as cursor:
                    cursor.execute("""
                        SELECT 
                            s.subscription_type,
                            s.start_date,
                            s.end_date,
                            u.signup_date
                        FROM users u
                        LEFT JOIN subscriptions s 
                            ON u.email = s.email AND s.is_active = TRUE
                        WHERE u.email = %s
                        ORDER BY s.end_date DESC
                        LIMIT 1
                    """, (st.session_state.email,))
                    subscription_data = cursor.fetchone()

            current_time = dt.now(timezone.utc)
            
            if subscription_data:
                sub_type = subscription_data[0]
                sub_start = subscription_data[1]
                sub_end = subscription_data[2]
                signup_date = subscription_data[3]

                # Convert naive datetimes to aware
                if sub_end and sub_end.tzinfo is None:
                    sub_end = sub_end.replace(tzinfo=timezone.utc)
                if signup_date and signup_date.tzinfo is None:
                    signup_date = signup_date.replace(tzinfo=timezone.utc)

                if sub_type == 'premium' and sub_end:
                    st.markdown(f"""
                        ### 🎉 Premium Membership
                        **Status**: {'Active' if current_time < sub_end else 'Expired'}  
                        **Expiry Date**: {sub_end.strftime('%Y-%m-%d')}
                    """)
                else:
                    if signup_date:
                        trial_end = signup_date + timedelta(days=7)
                        if current_time < trial_end:
                            remaining_days = (trial_end - current_time).days
                            st.markdown(f"""
                                ### Free Trial
                                **Remaining Days**: {remaining_days} days  
                                **Expiry**: {trial_end.strftime('%Y-%m-%d')}
                            """)
                        else:
                            st.markdown("""
                                ### Account Status
                                ⚠️ Your free trial has expired
                            """)
                    else:
                        st.markdown("""
                            ### Account Status
                            ⚠️ No active subscription
                        """)
            else:
                st.markdown("""
                    ### Account Status
                    ⚠️ No subscription data found
                """)

            if st.button("✨ Manage Subscription", type="primary", key="upgrade_btn"):
                checkout_url = create_checkout_session(st.session_state.email)
                if checkout_url:
                    st.markdown(f"""<meta http-equiv="refresh" content="0; url='{checkout_url}'" />""", 
                        unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error loading account data: {str(e)}")
            
    else:
        col1, col2, col3, col4, col5 = st.columns([1, 1.3, 1.3, 1.1, 1])
        with col3:    
            st.markdown("""
                <style>
                    div[data-testid="stForm"] {
                        margin: 1rem auto;
                        border: 2px solid #85C4E1FF;
                        background-color: white;
                        box-shadow: 5px 5px 15px rgba(0, 0.5, 0.5, 0.5);
                        padding: 2rem;
                        max-width: 600px;
                        width: 90%;
                    }
                    h3.fancy-header {
                        margin-left: 3.8rem !important;
                        color: #091E63FF !important;
                        font-size: 2rem;
                        margin-bottom: 1rem !important;
                    }
                    @media (max-width: 480px) {
                        div[data-testid="stForm"] {
                            padding: 1rem !important;
                            width: 100%;
                        }
                    }
                </style>
            """, unsafe_allow_html=True)

            with st.form(key="auth_form"):
                st.markdown(f"<h3 class='fancy-header'>{st.session_state.form_choice}</h3>", unsafe_allow_html=True)

                if st.session_state.form_choice == "Login":
                    email = st.text_input('Email', key="login_email")
                    password = st.text_input('Password', type='password', key="login_password")

                    col1, col_space, col2 = st.columns([1.5, 0.8, 1.8])
                    with col1:
                        login_submitted = st.form_submit_button("Login")
                    with col2:
                        signup_submitted = st.form_submit_button("Sign Up")

                    if login_submitted:
                        if not all([email, password]):
                            st.error("Please fill in all fields.")
                        elif not is_valid_email(email):
                            st.error("Invalid email format.")
                        else:
                            login(email, password)
                    
                    if signup_submitted:
                        st.session_state.form_choice = "Sign Up"
                        st.rerun()

                elif st.session_state.form_choice == "Sign Up":
                    email = st.text_input('Email', key="signup_email")
                    username = st.text_input('User Name', key="signup_username")
                    password = st.text_input('Password', type='password', key="signup_password")
                    confirm_password = st.text_input('Confirm Password', type='password', key="signup_confirm_password")

                    col1, col2 = st.columns([0.8, 0.8])
                    with col1:
                        signup_submitted = st.form_submit_button("Create my account")
                    with col2:
                        back_submitted = st.form_submit_button("Go back to Login")

                    if signup_submitted:
                        if not all([email, username, password, confirm_password]):
                            st.error("Please fill in all fields.")
                        elif password != confirm_password:
                            st.error("Passwords do not match.")
                        elif not is_password_strong(password):
                            st.error("Password must be at least 8 characters with letters, numbers, and special chars.")
                        elif create_user(email, username, password):
                            st.success("Account created! Please login.")
                            st.session_state.form_choice = "Login"
                            st.rerun()
                        else:
                            st.error("Account creation failed. Email may exist.")

                    if back_submitted:
                        st.session_state.form_choice = "Login"
                        st.rerun()

    display_footer()