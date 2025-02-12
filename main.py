import streamlit as st
from datetime import datetime as dt, timedelta, timezone
import time

# Set page config FIRST
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. INITIALIZE SESSION STATE FIRST -------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'email' not in st.session_state:
    st.session_state.email = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role_id' not in st.session_state:
    st.session_state.role_id = None 
if 'subscription_type' not in st.session_state:
    st.session_state.subscription_type = 'free'  # default
if 'signup_date' not in st.session_state:
    st.session_state.signup_date = None

# 2. IMPORT MODULES AFTER SESSION STATE INITIALIZATION ------


from app.admin import run as admin_run
from app.config import cookie_controller
import app.accounts as accounts
from app.home import run as home_run
from app.sidebar import render_sidebar  # common sidebar

class MultiApp:
    def __init__(self, selected_page):
        # Dictionary of pages
        self.pages = {
            "Home": home_run,
            "Account": accounts.run,
            "Admin": admin_run
        }
        # Check trial period for free users
        if (st.session_state.authenticated 
            and selected_page == "Home"
            and st.session_state.subscription_type == 'free'):
            
            signup_date = st.session_state.get('signup_date')
            if signup_date:
                # Ensure signup_date is timezone-aware
                if signup_date.tzinfo is None:
                    signup_date = signup_date.replace(tzinfo=timezone.utc)
                
                trial_end = signup_date + timedelta(days=7)
                current_time = dt.now(timezone.utc)

                if current_time > trial_end:
                    st.session_state.form_choice = "Payment"
                    selected_page = "Account"

        # Run the selected page
        if selected_page in self.pages:
            self.pages[selected_page]()
        else:
            home_run()

def main():
    # Render the sidebar once
    selected_page = render_sidebar()

    # Initialize MultiApp
    app = MultiApp(selected_page)

if __name__ == "__main__":
    # Session and auth checks
    accounts.check_session()
    st.session_state.setdefault('role_id', None)
    st.session_state.setdefault('authenticated', False)
    st.session_state.setdefault('signup_date', None)
    
    # DEVELOPMENT OVERRIDES (for testing)
    IS_DEV = False
    if IS_DEV:
        st.session_state.update({
            'authenticated': True,
            'email': 'dev@gmail.com',
            'username': 'Developer',
            'role_id': 1,
            'signup_date': dt.now(timezone.utc),  # Ensuring UTC
            'subscription_type': 'free'
        })
        cookie_controller.set("session_token", "dev_token", max_age=60*60*24)

    # If not in dev mode and not authenticated, run the accounts page and stop further execution.
    if not IS_DEV and not st.session_state.authenticated:
        accounts.run()
        st.stop()

    # Run the main app
    main()