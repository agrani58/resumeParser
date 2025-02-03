from datetime import datetime, timedelta, timezone

from streamlit import secrets
from config import cookie_controller  # Changed import
from connection import create_connection, create_session_token, create_user, delete_session_token, verify_user
from home import clear_user_files
from libraries import *
from ats import convert_docx_to_pdf
from PyPDF2 import PdfReader
from collections import defaultdict 
from json_file import resume_details, display_parsed_data, count_na 
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import secrets

# Remove circular imports
# Keep the rest of your existing home.py code

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
def is_password_strong(password):
    return (len(password) >= 8 and 
            any(c.isdigit() for c in password) and 
            any(c.isalpha() for c in password) and 
            any(c in "!@#$%^&*()-_" for c in password))

def check_session():
    # Initialize cookies if they don't exist
    if not hasattr(cookie_controller, '_CookieController__cookies') or cookie_controller._CookieController__cookies is None:
        st.session_state.authenticated = False
        return False

    # Check for session token
    session_token = cookie_controller.get("session_token")
    if not session_token:
        st.session_state.authenticated = False
        return False

    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.email, u.username FROM user_sessions s
                JOIN users u ON s.email = u.email
                WHERE s.session_token = %s AND s.expires_at > UTC_TIMESTAMP()
            """, (session_token,))
            if session := cursor.fetchone():
                st.session_state.update({
                    'authenticated': True,
                    'email': session[0],
                    'username': session[1]
                })
                return True
    except Exception as e:
        print(f"Session error: {e}")

    st.session_state.authenticated = False
    return False
from datetime import datetime, timedelta, timezone

def login(email, password):
    st.session_state.pop("uploaded_file", None)
    st.session_state.pop("parsed_data", None)
    st.session_state.pop("na_count", None)
    clear_user_files()
    user_key = f"user_{st.session_state.email}"
    if user_key in st.session_state:
        del st.session_state[user_key]
        
    if not (verification := verify_user(email, password)).get('status'):
        return st.error("Login failed. Check your credentials.")
    
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # Now works properly
    
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

def logout():
    clear_user_files()
    if session_token := cookie_controller.get("session_token"):
        delete_session_token(session_token)
        cookie_controller.set("session_token", "", max_age=0)
    keys_to_keep = ['_pages', '_last_page']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.session_state.pop("authenticated", None)
    st.session_state.pop("email", None)
    st.session_state.pop("username", None)
    st.success("Logged out successfully!")
    time.sleep(0.5)
    st.rerun()
def run():
    components()
    
    st.session_state.setdefault('authenticated', False)
    st.session_state.setdefault('form_choice', 'Login')
    st.session_state.setdefault('username', None)

    check_session()

    if st.session_state.authenticated:
        st.subheader(f"Welcome {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            logout()
    else:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # Preserved original styling
            st.markdown("""
                <style>
                    div[data-testid="stForm"] {
                        background: linear-gradient(135deg, #B0CDEAFF, #2A4FBFFF);
                        padding: 2rem;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        border: 1px solid #ccc;
                    }.fancy-header {
                        text-align: center;
                        color: #1d3557;
                        font-size: 26px;
                        margin-bottom: 1.5rem;
                        font-weight: bold;
                    }
                </style>
            """, unsafe_allow_html=True)

            with st.form(key="auth_form"):
                st.markdown(f"<h3 class='fancy-header'>{st.session_state.form_choice}</h3>", unsafe_allow_html=True)

                if st.session_state.form_choice == "Login":
                    email = st.text_input('Email', key="login_email")
                    password = st.text_input('Password', type='password', key="login_password")

                    # Preserved original column layout
                    col1, col_space, col2 = st.columns([1, 1.9, 1])
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

                    # Preserved original button layout
                    col1, col2 = st.columns([1, 0.717])
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