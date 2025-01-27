from libraries import *

def components():
    # page background colors
    page_bg_color ="""
    <style>
    .stApp {
        background-color: #f0f8ff; /* Light blue color */
    }
    </style>"""
    st.markdown(page_bg_color, unsafe_allow_html=True)

    sidebar_bg_color= """
    <style>
        .css-1d391kg { 
        background-color: #E5ECE9; 
    }
    </style>"""
    st.markdown(sidebar_bg_color , unsafe_allow_html=True)
    #back ground color ends
    try:
        
        col1, col2, col3 = st.columns([1, 2, 1])  # Create 3 columns for alignment
        with col2:  
                    
            st.markdown("<style>img {margin-top: -50px; margin-left: -75px }</style>", unsafe_allow_html=True)
            st.image("Logo/logo2.png",caption="           ", width=500)  
            st.markdown("<div style ='margin-top: -30px; margin-left:110px;'> <p>AI Resume Parser</p></div>", unsafe_allow_html=True)
                    
    except FileNotFoundError:
            st.error("Image file not found!")    



# from model import extract_text_from_pdf, process_resume_with_model
#e63946 red , yellow #f1faee, blue #a8dadc, bluedark #457b9d, darkest blue #1d3557
#importing the html components

