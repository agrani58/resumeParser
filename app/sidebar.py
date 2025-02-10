import streamlit as st
from streamlit_option_menu import option_menu
from app.accounts import logout

def render_sidebar():
    if st.session_state.get("role_id") == 2:
        return "Admin"
    
    with st.sidebar:
        # For a regular user (role_id == 1), show Account/Home navigation.
        if st.session_state.get("role_id") == 1:
            selected_page = option_menu(
                menu_title=None,
                options=["Account", "Home"],
                icons=["person-circle", "house"],
                default_index=0,
                styles={
                    "container": {"background-color": "#FFFFFFFF"},
                    "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#EEF8E1FF"},
                    "nav-link-selected": {"background-color": "#457b9d"}
                },
            )
        # For an admin user (role_id == 2), default to Admin.
        elif st.session_state.get("role_id") == 2:
            selected_page = "Admin"
        else:
            selected_page = "Home"
        
        # Render the logout button if the user is authenticated.
        if st.session_state.get("authenticated"):
            if st.button("Logout", key="logout_button"):
                logout()
        
        return selected_page
