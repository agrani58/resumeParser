import streamlit as st
from streamlit_option_menu import option_menu
from app.accounts import logout

def render_sidebar():
    selected_page = "Home"  # Default page
    
    if st.session_state.get("authenticated") and st.session_state.get("role_id") == 2:
        return "Admin"
    
    with st.sidebar:
        if st.session_state.get("authenticated"):
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

            
            # Logout button (independent of page selection)
            st.markdown("---")
            if st.button("Logout", key="logout_button"):
                logout()
                
        else:
            selected_page = "Home"
    
    return selected_page