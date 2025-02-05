import streamlit as st

def components():
    """Components that should only be visible after login"""
    
    # Hide Streamlit's default menu and footer
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Page background color
    page_bg_color = """
    <style>
    .stApp {
        background-color: #f0f8ff; /* Light blue color */
    }
    </style>
    """
    st.markdown(page_bg_color, unsafe_allow_html=True)

    # Sidebar background color
    sidebar_bg_color = """
    <style>
    [data-testid="stSidebar"]{ 
        # min-width: 210px !important;
        # max-width: 210px !important;
        background-color: #E5ECE9; 
    }
    </style>
    """
    st.markdown(sidebar_bg_color, unsafe_allow_html=True)

    col1, col2, col3 ,col4,col5= st.columns([1, 1, 2.2, 1,1])  # Create 3 columns for alignment
    with col3:
            st.markdown(
                "<style>img {margin-top: -80px;  }</style>", 
                unsafe_allow_html=True
            )
            st.image("Logo/logo2.png", caption=" ", width=500)
            st.markdown(
                "<div style='margin-top: -30px;width:100%; margin-left:185px'>"
                "<p>AI Resume Parser</p></div>", 
                unsafe_allow_html=True
            
            )