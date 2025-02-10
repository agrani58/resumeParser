import streamlit as st

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

# 2. IMPORT MODULES AFTER SESSION STATE INITIALIZATION ------
from app.config import cookie_controller
import app.accounts as accounts
from app.home import run as home_run
from app.sidebar import render_sidebar  # common sidebar
import app.admin as admin  # admin page module

class MultiApp:
    def __init__(self):
        # Dictionary of pages
        self.pages = {
            "Home": home_run,
            "Account": accounts.run,
            "Admin": admin.run
        }
        # Render the common sidebar (which includes the navigation and logout button)
        self.current_page = render_sidebar()

        # Additional logic: e.g. force Payment page if free user has reached upload limit.
        if (st.session_state.authenticated 
            and self.current_page == "Home"
            and st.session_state.subscription_type == 'free'):
            from app.schema import get_upload_count
            if get_upload_count(st.session_state.email) >= 3:
                st.session_state.form_choice = "Payment"
                self.current_page = "Account"

        # Run the selected page.
        if self.current_page in self.pages:
            self.pages[self.current_page]()
        else:
            home_run()

    def run(self):
        """Main app runner (not used separately here since __init__ already runs the page)"""
        current_page = self.current_page
        if st.session_state.authenticated:
            if current_page in self.pages:
                self.pages[current_page]()
            else:
                home_run()
        else:
            accounts.run()

if __name__ == "__main__":
    # Session and auth checks
    accounts.check_session()
    st.session_state.setdefault('role_id', None)
    st.session_state.setdefault('authenticated', False)
    
    # DEVELOPMENT OVERRIDES (for testing)
    IS_DEV = True
    if IS_DEV:
        st.session_state.update({
            'authenticated': True,
            'email': 'dev@gmail.com',
            'username': 'Developer',
            'role_id': 2
        })
        cookie_controller.set("session_token", "dev_token", max_age=60*60*24)

    # If not in dev mode and not authenticated, run the accounts page and stop further execution.
    if not IS_DEV and not st.session_state.authenticated:
        accounts.run()
        st.stop()

    # Run the MultiApp.
MultiApp()
