from libraries import *

def components():
    st.set_page_config(
        page_title="Resume Parser",
        page_icon='Logo\logo.png',
    )

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

    st.sidebar.markdown("Choose user")
    activities=["User","Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:",activities)
    if choice == 'User':
            try:
                # Displaying the image in the center using st.image
                col1, col2, col3 = st.columns([1, 2, 1])  # Create 3 columns for alignment
                with col2:  # Place the image in the middle column
                    
                    st.markdown("<style>img {margin-top: -50px; margin-left: -75px }</style>", unsafe_allow_html=True) #img represents all images so it brings all img to -50 
                    st.image("Logo/logo2.png",caption="           ", width=500)  
                    st.markdown("<div style ='margin-top: -30px; margin-left:110px;'> <p>AI Resume Parser</p></div>", unsafe_allow_html=True)
                    
            except FileNotFoundError:
                st.error("Image file not found!")    
            st.markdown('''<div style='margin-top: 20px; margin-left: 265px; margin-bottom: -40px'> <h5 style='color:#1d3557;'>Upload your Resume</h5>
            </div>''', unsafe_allow_html=True)
