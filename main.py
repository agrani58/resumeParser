# main.py
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

# 2. IMPORT MODULES AFTER SESSION STATE INITIALIZATION ------
from app.config import cookie_controller
import app.accounts as accounts
from streamlit_option_menu import option_menu
from app.home import run as home_run

class MultiApp:
    def __init__(self):
        self.pages = {
            "Home": home_run,
            "Account": accounts.run
        }
    
    def nav_sidebar(self):
        """Render navigation in sidebar"""
        with st.sidebar:
            if st.session_state.authenticated:
                params = st.query_params
                selected_page = params.get("page", ["Home"])[0]
                
                app = option_menu(
                    menu_title=None,
                    options=[ 'Account','Home'],
                    icons=[ 'person-circle','house'],
                    default_index=0 if selected_page == "Home" else 1,
                    styles={
                        "container": {"background-color": "white"},
                        "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#f1faee"},
                        "nav-link-selected": {"background-color": "#457b9d"},
                    }
                )
                st.query_params["page"] = app
                return app
            return "Account"

    def run(self):
        """Main app runner"""
        current_page = self.nav_sidebar()
        
        # Render main content area
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
    
    # DEVELOPMENT OVERRIDES
    IS_DEV = False
    if IS_DEV:
        st.session_state.update({
            'authenticated': True,
            'email': 'dev@example.com',
            'username': 'Developer'
        })
        cookie_controller.set("session_token", "dev_token", max_age=60*60*24)

    # Run the app
    if not IS_DEV and not st.session_state.authenticated:
        accounts.run()
        st.stop()  # Prevent further execution
    
    MultiApp().run()