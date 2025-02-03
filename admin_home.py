import streamlit as st

def run():
    st.title("Admin Dashboard")
    st.write("Welcome Admin!")
    
    # Add admin-specific functionality here
    st.write("Admin-only features:")
    st.write("- User management")
    st.write("- System analytics")
    st.write("- Content moderation")
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.role_id = None
        st.rerun()