import streamlit as st
import os
import time
import base64
from PyPDF2 import PdfReader
from app.libraries import *  # your additional libraries
from app.config import cookie_controller
from app.schema import create_connection, delete_session_token, save_resume_analysis
from app.utils import count_na, is_valid_date, resume_details, resume_score
from app.view import display_footer, display_parsed_data, display_tips
from app.components import components  # Use components() for home page

def get_user_upload_dir():
    if not st.session_state.get('authenticated'):
        return None
    return os.path.join('./Uploaded_Resumes', st.session_state.email)

def convert_docx_to_pdf(docx_resume_path):
    if docx_resume_path.endswith(".docx"):
        try:
            import pythoncom, comtypes.client
            pythoncom.CoInitialize()
            uploaded_resume_path = os.path.splitext(docx_resume_path)[0] + ".pdf"
            word = comtypes.client.CreateObject("Word.Application")
            word.Visible = False
            in_file = word.Documents.Open(docx_resume_path)
            in_file.SaveAs(uploaded_resume_path, FileFormat=17)
            in_file.Close()
            word.Quit()
            return uploaded_resume_path
        except Exception as e:
            st.error(f"An error occurred during conversion: {e}")
            return None
        finally:
            pythoncom.CoUninitialize()

def show_resume(uploaded_resume_path):
    try:
        with open(uploaded_resume_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'''
                <div style="width: 100%; height: 700px; overflow: auto;">
                    <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="100%" style="border: none;"></iframe>
                </div>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying resume: {e}")

def extract_text_from_pdf(uploaded_resume_path):
    try:
        with open(uploaded_resume_path, "rb") as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                if page_text := page.extract_text():
                    text += page_text
            if not text.strip():
                st.error("PDF appears to be image-based - text extraction failed")
                return None
            return resume_details(text)
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def clear_user_files():
    user_dir = get_user_upload_dir()
    if user_dir and os.path.exists(user_dir):
        for f in os.listdir(user_dir):
            os.remove(os.path.join(user_dir, f))
        os.rmdir(user_dir)

def run():
    # Render home page UI components (background, logo, etc.)
    components()
    
    # If user is free and reached upload limit, force upgrade.
    if st.session_state.get('authenticated') and st.session_state.get('subscription_type', 'free') == 'free':
        from app.schema import get_upload_count
        upload_count = get_upload_count(st.session_state.email)
        if upload_count >= 3:
            st.error("You've reached your monthly limit of 3 free uploads. 🔒")
            col1, col2 = st.columns([1, 3])
            with col2:
                if st.button("✨ Upgrade to Premium for Unlimited Uploads", type="primary", key="upgrade_button_home"):
                    st.session_state.form_choice = "Payment"
                    st.rerun()
            st.stop()
    st.session_state.setdefault('uploaded_file', None)
    st.session_state.setdefault('parsed_data', None)
    st.session_state.setdefault('na_count', 0)
    st.session_state.setdefault('resume_path', None)

    from app.accounts import check_session, run as accounts_run
    check_session()
    if not st.session_state.get('authenticated'):
        st.warning("Please login first!")
        accounts_run()  # Redirect to login/signup page.
        st.stop()

    user_dir = get_user_upload_dir()
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    if not st.session_state.get('resume_path'):
        existing_files = [f for f in os.listdir(user_dir) if f.lower().endswith(('.pdf', '.docx'))]
        if existing_files:
            latest_file = max(existing_files, key=lambda x: os.path.getmtime(os.path.join(user_dir, x)))
            st.session_state.resume_path = os.path.join(user_dir, latest_file)

    if st.session_state.get('resume_path') and not st.session_state.get('parsed_data'):
        resume_text = extract_text_from_pdf(st.session_state.resume_path)
        if resume_text:
            st.session_state.parsed_data = resume_details(resume_text)
            st.session_state.na_count = count_na(st.session_state.parsed_data)[0]
            if save_resume_analysis(st.session_state.email, st.session_state.parsed_data):
                placeholder = st.empty()
            else:
                st.error("Failed to save resume data to database.")

    col1, col2, col3 = st.columns([1.4, 0.002, 1.4])
    with col1:
        st.markdown(
            '''<div style='margin-top:5rem;margin-bottom:-30px; text-align: center;'>
                <h5 style='color: #1d3557;'>Upload Your Resume</h5>
            </div>''',
            unsafe_allow_html=True
        )
        # Use a unique key for the file uploader
        file_uploaded = st.file_uploader(" ", type=["pdf", "docx"], key="file_uploader")
        placeholder = st.empty()
        if file_uploaded and (file_uploaded != st.session_state.get('uploaded_file')):
            for f in os.listdir(user_dir):
                os.remove(os.path.join(user_dir, f))
            placeholder.success("Resume uploaded successfully!")
            time.sleep(2)
            file_extension = file_uploaded.name.split('.')[-1].lower()
            uploaded_resume_path = os.path.join(user_dir, file_uploaded.name)
            with open(uploaded_resume_path, "wb") as f:
                f.write(file_uploaded.getbuffer())
            if file_extension == "docx":
                converted_pdf_path = convert_docx_to_pdf(uploaded_resume_path)
                if converted_pdf_path:
                    uploaded_resume_path = converted_pdf_path
                else:
                    st.error("Failed to convert DOCX to PDF.")
                    return
            st.session_state.resume_path = uploaded_resume_path
            st.session_state.uploaded_file = file_uploaded
            st.session_state.parsed_data = None  # Reset parsed data to trigger reprocessing
            st.rerun()
        if st.session_state.get('resume_path') and os.path.exists(st.session_state.resume_path):
            show_resume(st.session_state.resume_path)
    with col3:
        if st.session_state.get('parsed_data'):
            na_count, na_paths = count_na(st.session_state.parsed_data)
            st.session_state.na_count = na_count
            display_parsed_data(st.session_state.parsed_data, missing_fields=na_paths)
    if st.session_state.get('parsed_data'):
        parsed_data = st.session_state.parsed_data
        tips_data = {
            'na_count': st.session_state.na_count,
            'suggested_category': parsed_data.get("Suggested_Resume_Category", ""),
            'applied_profile': parsed_data.get("Applied_for_Profile", ""),
            'invalid_dates_count': sum(1 for edu in parsed_data.get("Education", [])
                                    if not is_valid_date(edu.get('Graduation_Date', ''))),
            'applied_profile ': parsed_data.get("Applied_for_Profile", "").lower(),
            'resume_score': resume_score(parsed_data),
            'Recommended_Additional_Skills': parsed_data.get("Recommended_Additional_Skills", [])
        }
        display_tips(tips_data, missing_fields=na_paths)
    display_footer()