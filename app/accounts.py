import streamlit as st
import time
import secrets
import re
from datetime import datetime, timedelta, timezone

from app.config import cookie_controller
from app.schema import create_connection, create_session_token, create_user, delete_session_token, verify_user, save_resume_analysis
from app.home import clear_user_files
from app.components import main_components  # For Accounts/Admin pages
from app.view import display_footer

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def is_password_strong(password):
    return (len(password) >= 3 and any(c in "!@#$%^&*()-_" for c in password))

def check_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    session_token = cookie_controller.get("session_token")
    if not session_token:
        st.session_state.authenticated = False
        return False
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.email, u.username, u.role_id
                FROM user_sessions s
                JOIN users u ON s.email = u.email
                WHERE s.session_token = %s AND s.expires_at > UTC_TIMESTAMP()
            """, (session_token,))
            if session := cursor.fetchone():
                st.session_state.update({
                    'authenticated': True,
                    'email': session[0],
                    'username': session[1],
                    'role_id': session[2]
                })
                return True
    except Exception as e:
        st.error(f"Session error: {e}")
    return False

def login(email, password):
    verification = verify_user(email, password)
    if not verification or not isinstance(verification, dict) or not verification.get('status'):
        return st.error("Login failed. Check your credentials.")
    if verification['status']:
        st.session_state.authenticated = True
        st.session_state.email = email
        st.session_state.username = verification['username']
        st.session_state.role_id = verification['role_id']
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    if create_session_token(email, session_token, expires_at):
        cookie_controller.set("session_token", session_token,
            max_age=int((expires_at - datetime.now(timezone.utc)).total_seconds()))
        st.session_state.update({
            'authenticated': True,
            'email': email,
            'username': verification.get('username', 'User')
        })
        st.success("Logged in successfully!")
        time.sleep(0.5)
        st.rerun()
    else:
        st.error("Failed to create session. Please try again.")
import stripe
import streamlit as st

def create_checkout_session():
    stripe.api_key = st.secrets["stripe"]["secret_key"]
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1QqzjsD1iUPBafNcjG7nN4pM',  # Replace with your price ID
                'quantity': 1,
            }],
            mode='subscription',
            success_url = st.secrets["app"]["base_url"] + '/success',
            cancel_url = st.secrets["app"]["base_url"] + '/cancel',
            customer_email=st.session_state.email,
        )
        return checkout_session.url
    except Exception as e:
        st.error(f"Error creating checkout session: {e}")
        return None
def logout():
    clear_user_files()
    if session_token := cookie_controller.get("session_token"):
        delete_session_token(session_token)
        cookie_controller.set("session_token", "", max_age=0)
    # Clear all session state keys.
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.authenticated = False
    st.rerun()

def run():
    # Use main_components() for Accounts page.
    main_components()
    st.session_state.setdefault('authenticated', False)
    st.session_state.setdefault('form_choice', 'Login')
    st.session_state.setdefault('username', None)
    check_session()

    if st.session_state.authenticated:
        st.subheader(f"Welcome {st.session_state.username}!")

        # Add Payment UI for Free Users
        if st.session_state.get('subscription_type') == 'free':
            st.markdown("### Upgrade to Premium")
            st.write("Unlock unlimited uploads by upgrading to a premium subscription.")
            if st.button("✨ Upgrade to Premium for Unlimited Uploads", type="primary", key="upgrade_button"):
                checkout_url = create_checkout_session()
                if checkout_url:
                    st.write(f"Please complete your payment [here]({checkout_url}).")
                else:
                    st.error("Failed to create checkout session. Please try again.")
    else:
        col1, col2, col3, col4, col5 = st.columns([1, 1.3, 1.3, 1.1, 1])
        with col3:
            st.markdown("""
                <style>
                    div[data-testid="stForm"] {
                        margin: 1rem auto;
                        border: 2px solid #85C4E1FF;
                        background-color: white;
                        box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.5);
                        padding: 2rem;
                        max-width: 600px;
                        width: 90%;
                    }
                    h3.fancy-header {
                        margin-left:3.8rem!important;
                        color: #091E63FF !important;
                        font-size: 2rem;
                        margin-bottom: 1rem !important;
                    }
                    .stTextInput>div>div>input,
                    .stTextInput>div>div>input:focus {
                        width: 100% !important;
                        min-width: unset !important;
                    }
                    @media (max-width: 480px) {
                        div[data-testid="stForm"] {
                            padding: 1rem !important;
                            min-height: 300px;
                            width: 100%;
                            margin: 0.5rem auto;
                        }
                        .stForm .col-container {
                            flex-direction: column !important;
                        }
                    }
                </style>
            """, unsafe_allow_html=True)
            with st.form(key="auth_form_accounts"):
                st.markdown(f"<h3 class='fancy-header'>{st.session_state.form_choice}</h3>", unsafe_allow_html=True)
                if st.session_state.form_choice == "Login":
                    email = st.text_input('Email', key="login_email_accounts")
                    password = st.text_input('Password', type='password', key="login_password_accounts")
                    col1a, col_space, col2a = st.columns([1.5, 0.8, 1.8])
                    with col1a:
                        login_submitted = st.form_submit_button("Login")
                    with col2a:
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
                    email = st.text_input('Email', key="signup_email_accounts")
                    username = st.text_input('User Name', key="signup_username_accounts")
                    password = st.text_input('Password', type='password', key="signup_password_accounts")
                    confirm_password = st.text_input('Confirm Password', type='password', key="signup_confirm_password_accounts")
                    col1b, col2b = st.columns([0.8, 0.8])
                    with col1b:
                        signup_submitted = st.form_submit_button("Create my account")
                    with col2b:
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
