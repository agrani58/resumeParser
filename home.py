import os
import base64
import time
import streamlit as st
from PyPDF2 import PdfReader
import accounts
from components import components
from config import cookie_controller
from connection import delete_session_token
from json_file import resume_details, display_parsed_data, count_na
from ats import convert_docx_to_pdf

def get_user_upload_dir():
    """Get the user-specific upload directory."""
    if 'email' in st.session_state and st.session_state.email:
        return os.path.join('./Uploaded_Resumes', st.session_state.email)
    return None

def show_resume(uploaded_resume_path):
    """Display the uploaded resume PDF."""
    try:
        with open(uploaded_resume_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            # Use CSS to make the iframe responsive
            pdf_display = f'''
                <div style="width: 100%; height: 700px; overflow: auto;">
                    <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="100%" style="border: none;"></iframe>
                </div>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying resume: {e}")
def extract_text_from_pdf(uploaded_resume_path):
    """Extract text from the uploaded resume."""
    try:
        with open(uploaded_resume_path, "rb") as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return resume_details(text)
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def clear_user_files():
    """Clear uploaded files on logout."""
    user_dir = get_user_upload_dir()
    if user_dir and os.path.exists(user_dir):
        for f in os.listdir(user_dir):
            os.remove(os.path.join(user_dir, f))
        os.rmdir(user_dir)

def run():
    components()
    
    # Initialize session state for file and analysis
    st.session_state.setdefault('uploaded_file', None)
    st.session_state.setdefault('parsed_data', None)
    st.session_state.setdefault('na_count', 0)
    st.session_state.setdefault('resume_path', None)  # Add this to store the file path

    # Check authentication
    if not st.session_state.get('authenticated'):
        st.warning("Please login first!")
        accounts.run()
        return
        
    user_dir = get_user_upload_dir()
        # Ensure directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    if not user_dir:
        st.error("User directory not available. Please log in again.")
        return

    # Ensure directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    # Handle logout
    if st.sidebar.button("Logout"):
        clear_user_files()
        if 'uploaded_file' in st.session_state:
            del st.session_state.uploaded_file
        if 'parsed_data' in st.session_state:
            del st.session_state.parsed_data
        if 'na_count' in st.session_state:
            del st.session_state.na_count
        if 'resume_path' in st.session_state:
            del st.session_state.resume_path
        session_token = cookie_controller.get("session_token")
        if session_token:
            delete_session_token(session_token)
            cookie_controller.set("session_token", "", max_age=0)
        st.session_state.authenticated = False
        st.session_state.pop("email", None)
        st.rerun()
        
        
    col1, col2,col3 = st.columns([1.4,0.002,1.4])  # Adjusted ratios for better responsiveness

    # Main UI   
    with col1:
        st.markdown(
            '''<div style='margin-top:60px; text-align: center;'>
                <h4 style='color: #1d3557;'>Upload Your Resume</h4>
            </div>''',
            unsafe_allow_html=True
        )

        # File uploader with unique key
        file_uploaded = st.file_uploader(" ", type=["pdf", "docx"], key="persistent_uploader")
        placeholder = st.empty()
    # Process new upload
        if file_uploaded and (file_uploaded != st.session_state.uploaded_file):
            st.session_state.uploaded_file = file_uploaded
            st.session_state.parsed_data = None
            st.session_state.na_count = 0

            # Save the file
            file_extension = file_uploaded.name.split('.')[-1].lower()
            uploaded_resume_path = os.path.join(user_dir, file_uploaded.name)
            
            if not os.path.exists(uploaded_resume_path):
                with open(uploaded_resume_path, "wb") as f:
                    f.write(file_uploaded.getbuffer())
            placeholder.success("Resume uploaded successfully!")
            time.sleep(4)
            # Handle DOCX conversion
            if file_extension == "docx":
                converted_pdf_path = convert_docx_to_pdf(uploaded_resume_path)
                if converted_pdf_path:
                    uploaded_resume_path = converted_pdf_path
                    st.success("DOCX converted to PDF successfully!")
                else:
                    st.error("DOCX conversion failed.")

            # Store the file path in session state
            st.session_state.resume_path = uploaded_resume_path

            # Process text extraction
            with st.spinner("Extracting and parsing resume..."):
                resume_text = extract_text_from_pdf(uploaded_resume_path)
                if resume_text:
                    st.session_state.parsed_data = resume_details(resume_text)

        # Show existing resume and analysis if available
        if st.session_state.get('resume_path') and os.path.exists(st.session_state.resume_path):
            show_resume(st.session_state.resume_path)
    with col3:
        if st.session_state.get('parsed_data'):
            na_count, na_paths = count_na(st.session_state.parsed_data)
            st.session_state.na_count = na_count
            display_parsed_data(st.session_state.parsed_data, missing_fields=na_paths)

            # Display recommendations
            st.markdown(
                '''<div style='margin-top: 20px; text-align: center;'>
                    <h5 style='color: #1d3557;'>Resume Tips & Tricks</h5>
                </div>''',
                unsafe_allow_html=True
            )
            
            st.markdown(f"""
                <div style="margin-top: 20px; padding: 10px; background-color: #ffe6e6; border-radius: 25px; text-align: center;">
                    ⚠️ Found {st.session_state.na_count} missing fields. Include these to make your resume ATS compatible.
                </div>
            """, unsafe_allow_html=True)
    