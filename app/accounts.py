from datetime import datetime, timedelta, timezone

from streamlit import secrets
from app.config import cookie_controller  # Changed import
from app.schema import create_connection, create_session_token, create_user, delete_session_token, verify_user
from app.home import clear_user_files
from app.libraries import *
import secrets

from app.view import display_footer

# Remove circular imports
# Keep the rest of your existing home.py code

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
def is_password_strong(password):
    return (len(password) >= 3 and 
            # any(c.isdigit() for c in password) and 
            # any(c.isalpha() for c in password) and 
            any(c in "!@#$%^&*()-_" for c in password))


def check_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated =False
    
    # DEVELOPMENT BYPASS ==============================================
    # if cookie_controller.get("session_token") == "dev_token":
    #     st.session_state.update({
    #         'authenticated': False,
    #         'email': 'dev@example.com',
    #         'username': 'Developer'
    #     })
    #     return True
    # ================================================================
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
        st.error(f"Session error: {e}")
    return False


from datetime import datetime, timedelta, timezone

# accounts.py (updated login function)
def login(email, password):
    
    # Verify credentials
    verification = verify_user(email, password)
    if not verification or not isinstance(verification, dict) or not verification.get('status'):
        return st.error("Login failed. Check your credentials.")
    

    # Create new session
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
    keys_to_keep = []
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
            
    st.session_state.authenticated = False
    
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
        col1, col2, col3 = st.columns([1, 0.96, 1])
        with col2:
            # Add responsive CSS
            st.markdown("""
                <style>
                    @media (max-width: 600px) {
                        div[data-testid="stForm"] {
                            padding: 1rem !important;
                        }
                        .fancy-header {
                            font-size: 20px !important;
                        }
                        .stButton button {
                            width: 100% !important;
                            !important;
                        }
                    }
                    div[data-testid="stForm"] {
                        background: linear-gradient(135deg, #B0CDEAFF, #2A4FBFFF);
                        padding: 2rem;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        border: 1px solid #ccc;
                    }
                    .fancy-header {
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

                    # Use responsive columns
                    col1, col_space, col2 = st.columns([1.05, 1.95, 1])
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

                    # Use responsive columns
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
    display_footer()