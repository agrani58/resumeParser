import streamlit as st

# Set page config FIRST
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)
import accounts
from config import cookie_controller
# IS_DEV = False  # Set to False in production

# # Set development mode state FIRST
# if IS_DEV:
#     st.session_state.setdefault('authenticated', False)
#     st.session_state.setdefault('email', 'dev@example.com')
#     st.session_state.setdefault('username', 'Developer')
#     cookie_controller.set("session_token", "dev_token", max_age=60*60*24) 

# if not IS_DEV and not st.session_state.authenticated:
#     st.warning("Please login first!")
#     accounts.run()

# Initialize session state immediately after page config
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'email' not in st.session_state:
    st.session_state.email = None

# Now import other modules
from streamlit_option_menu import option_menu
from accounts import check_session, run as accounts_run
from home import run as home_run

# Check session state
check_session()
class MultiApp:
    def run(self):
        with st.sidebar:
            if st.session_state.authenticated:
                # Use st.query_params for URL parameter handling
                params = st.query_params
                initial_index = 0 if params.get("page", ["Home"])[0] == "Home" else 1
                
                app = option_menu(
                    menu_title=None,
                    options=['Home', 'Account'],
                    icons=['house', 'person-circle'],
                    default_index=initial_index,
                    key="main_menu",
                    styles={
                        "container": {"background-color": "white"},
                        "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#f1faee"},
                        "nav-link-selected": {"background-color": "#457b9d"},
                    }
                )
                
                # Update URL param using st.query_params
                if app == "Home":
                    st.query_params["page"] = "Home"
                else:
                    st.query_params["page"] = "Account"
            else:
                app = 'Account'

        if app == 'Account':
            accounts_run()
        elif app == 'Home' and st.session_state.authenticated:
            home_run()
# Initialize and run the app
if __name__ == "__main__":
    app = MultiApp()
    app.run()