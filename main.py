
import streamlit as st  # Import Streamlit right after setting page config
st.set_page_config(
    page_title="Resume Parser",
    page_icon='Logo/logo.png',
)

from libraries import *
from streamlit_option_menu import option_menu
import accounts, home


class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run(self):
        # Sidebar navigation menu
        with st.sidebar:
            app = option_menu(
                menu_title=None,  # No title for the sidebar
                options=['Account', 'Home'],  # Menu options
                default_index=0,  # Default selected option
                styles={
                    "container": { "background-color": "white"},
                    "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#f1faee"},
                    "nav-link-selected": {"background-color": "#457b9d"},
                }
            )

        # Navigate to the selected app
        if app == 'Account':
            accounts.run() 
        elif app == 'Home':
            home.run()

multi_app = MultiApp()
multi_app.add_app("Account", accounts.run)
multi_app.add_app("Home", home.run)

# Run the app
multi_app.run()
