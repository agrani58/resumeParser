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
    st.session_state.role_id = None  # Store user role

# 2. IMPORT MODULES AFTER SESSION STATE INITIALIZATION ------
from app.config import cookie_controller
import app.accounts as accounts
from streamlit_option_menu import option_menu
from app.home import run as home_run
import app.admin as admin  # Import the admin module
class MultiApp:
    def __init__(self):
        self.pages = {
            "Home": home_run,
            "Account": accounts.run,
            "Admin": admin.run  # Add the admin page
        }

    def nav_sidebar(self):
        """Render navigation in sidebar"""
        # Skip sidebar rendering if the current page is Admin
        if st.session_state.role_id == 2 and st.query_params.get("page", ["Home"])[0] == "Admin":
            return "Admin"  # Return "Admin" without rendering the sidebar

        # Render the sidebar for non-admin pages
        with st.sidebar:
            params = st.query_params
            selected_page = params.get("page", ["Home"])[0]

            # Render the sidebar for non-admin users
            if st.session_state.role_id == 1:
                app = option_menu(
                    menu_title=None,
                    options=["Account", "Home"],
                    icons=["person-circle", "house"],
                    default_index=0 if selected_page == "Home" else 1,
                    styles={
                        "container": {"background-color": "#FFFFFFFF"},
                        "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#EEF8E1FF"},
                        "nav-link-selected": {"background-color": "#457b9d"},
                    }
                )
                st.query_params["page"] = app
                return app

        return "Home"  # Default page if no sidebar is rendered

    def run(self):
        """Main app runner"""
        current_page = self.nav_sidebar()

        # ✅ If admin, allow access to Admin panel
        if st.session_state.authenticated and st.session_state.role_id == 2 and current_page == "Admin":
            admin.run()
            return  # Prevent other pages from loading

        # ✅ Normal users continue as usual
        if st.session_state.authenticated:
            if current_page in self.pages:
                self.pages[current_page]()
            else:
                home_run()
        else:
            accounts.run()

    def run(self):
        """Main app runner"""
        current_page = self.nav_sidebar()

        # ✅ If admin, allow access to Admin panel
        if st.session_state.authenticated and st.session_state.role_id == 2 and current_page == "Admin":
            admin.run()
            return  # Prevent other pages from loading

        # ✅ Normal users continue as usual
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
    
    # DEVELOPMENT OVERRIDES
    IS_DEV = False
    if IS_DEV:
        st.session_state.update({
            'authenticated': True,
            'email': 'dev@gmail.com',
            'username': 'Developer',
            'role_id': 2   })
        cookie_controller.set("session_token", "dev_token", max_age=60*60*24)

    # Run the app
    if not IS_DEV and not st.session_state.authenticated:
        accounts.run()
        st.stop()  # Prevent further execution

    MultiApp().run()

