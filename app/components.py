import streamlit as st

def components():
    """Components that should only be visible after login"""
    
    # Hide Streamlit's default menu and footer
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    background_image_url = "https://i.imgur.com/6K1RTOS.png"
    # Page background color
    page_bg_color = f"""
    
        <style>
        .stApp {{
            background: url("{background_image_url}");
            background-size: auto;  /* Ensures the image is not stretched */
            background-repeat: repeat; /* Repeat both horizontally and vertically */
            background-attachment: fixed; /* Keeps the background in place */
            # background: linear-gradient( 45deg,#F9F6F6FF, #F9F6F6FF,#90dbf4,#90dbf4); 

        }}
        </style>
        """
    st.markdown(page_bg_color, unsafe_allow_html=True)
    col1, col2, col3 ,col4,col5= st.columns([1, 1, 1.9, 1,1])  # Create 3 columns for alignment
    with col3:
        
            st.markdown(
                "<style>img {margin-top: -4rem;  }</style>", 
                unsafe_allow_html=True
            )
            st.image("Logo/logo2.png", caption=" ", width=500)
            st.markdown(
                "<div style='margin-top: -30px;width:100%; margin-left:185px'>"
                "<p>AI Resume Parser</p></div>", 
                unsafe_allow_html=True
            
        )
            


def main_components():
    """Components that should only be visible after login"""
    
    # Hide Streamlit's default menu and footer
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    background_image_url = "https://i.imgur.com/u0JDacq.png"
    # Page background color
    page_bg_color = f"""
    
        <style>
        .stApp {{
            background: url("{background_image_url}");
            background-size: auto;  /* Ensures the image is not stretched */
            background-repeat: repeat; /* Repeat both horizontally and vertically */
            background-attachment: fixed; /* Keeps the background in place */
            # background: linear-gradient( 45deg,#F9F6F6FF, #F9F6F6FF,#90dbf4,#90dbf4); 

        }}
        </style>
        """
    st.markdown(page_bg_color, unsafe_allow_html=True)

    col1, col2, col3 ,col4,col5= st.columns([1, 1, 1.9, 1,1])  # Create 3 columns for alignment
    with col3:
        
            st.markdown(
                "<style>img {margin-top: -4rem;  }</style>", 
                unsafe_allow_html=True
            )
            st.image("Logo/logo2.png", caption=" ", width=500)
            st.markdown(
                "<div style='margin-top: -30px;width:100%; margin-left:185px'>"
                "<p>AI Resume Parser</p></div>", 
                unsafe_allow_html=True
            
        )
            
    

