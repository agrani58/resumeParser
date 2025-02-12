from socket import create_connection
import streamlit as st
import os
from datetime import datetime as dt, timedelta, timezone
import time
import base64
from PyPDF2 import PdfReader
from app.libraries import *
from app.config import cookie_controller
from app.schema import get_connection, save_resume_analysis
from app.payments import create_checkout_session
from app.utils import count_na, is_valid_date, resume_details, resume_score
from app.view import display_footer, display_parsed_data, display_tips
from app.components import main_components
from dotenv import load_dotenv
load_dotenv()

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
    with open(uploaded_resume_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'''
            <div style="width: 100%; height: 700px; overflow: auto;">
                <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="100%" style="border: none;"></iframe>
            </div>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_resume_path):
    try:
        # Ensure the file exists
        if not os.path.exists(uploaded_resume_path):
            st.error("File not found. Please upload the file again.")
            return None

        # Open the PDF file
        with open(uploaded_resume_path, "rb") as file:
            reader = PdfReader(file)

            # Check if the PDF is encrypted
            if reader.is_encrypted:
                st.error("PDF is encrypted and cannot be processed.")
                return None

            # Extract text from each page
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # Ensure text is not None or empty
                    text += page_text

            # Check if any text was extracted
            if not text.strip():
                st.error("PDF appears to be image-based or contains no extractable text.")
                return None

            return text

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
    main_components()
    
    # Check subscription status
    if not st.session_state.get('authenticated'):
        st.warning("Please login to access this feature!")
        return

    # Get subscription status
    try:
        with get_connection() as conn:
            with conn.cursor(buffered=True) as cursor:
                cursor.execute("""
                    SELECT 
                        s.subscription_type, 
                        s.start_date, 
                        s.end_date,
                        u.signup_date
                    FROM users u
                    LEFT JOIN subscriptions s 
                        ON u.email = s.email AND s.is_active = TRUE
                    WHERE u.email = %s
                    ORDER BY s.end_date DESC
                    LIMIT 1
                """, (st.session_state.email,))
                result = cursor.fetchone()
                
                subscription_type = 'free'
                sub_end = None
                signup_date = None
                trial_end = None
                
                if result:
                    subscription_type = result[0] or 'free'
                    sub_start = result[1]
                    sub_end = result[2]
                    signup_date = result[3]
                    
                    # Calculate trial end (7 days from signup)
                    if signup_date:
                        trial_end = signup_date.replace(tzinfo=timezone.utc) + timedelta(days=7)
                    
    except Exception as e:
        st.error(f"Error checking subscription status: {e}")
        return

    current_time = dt.now(timezone.utc)
    subscription_active = False
    
    # Check subscription validity
    if subscription_type == 'premium' and sub_end:
        subscription_active = current_time < sub_end.replace(tzinfo=timezone.utc)
    elif subscription_type == 'free' and trial_end:
        subscription_active = current_time < trial_end
        
    # Handle free trial and premium expiration logic
    if not subscription_active:
        if subscription_type == 'free':
            st.error("🔒 Your free trial has ended!")
        else:
            st.error("🔒 Your subscription has expired!")
        
        if st.button("✨ Upgrade to Premium", type="primary"):
            checkout_url = create_checkout_session(st.session_state.email)
            if checkout_url:
                st.markdown(f"""<meta http-equiv="refresh" content="0; url='{checkout_url}'" />""", 
                          unsafe_allow_html=True)
        return
            
    elif subscription_type == 'premium':
        if sub_end:
            if sub_end.tzinfo is None:
                sub_end = sub_end.replace(tzinfo=timezone.utc)
            
            current_time = dt.now(timezone.utc)
            if current_time > sub_end:
                st.error("Your premium subscription has expired. 🔒")
                if st.button("✨ Renew Premium Subscription", type="primary"):
                    checkout_url = create_checkout_session(st.session_state.email)
                    if checkout_url:
                        st.write(f"Please complete payment [here]({checkout_url}).")
                    else:
                        st.error("Failed to create checkout session.")
                return  # Stop further execution if premium has expired

    # Only show uploader if user is premium or still in free trial
    st.session_state.setdefault('uploaded_file', None)
    st.session_state.setdefault('parsed_data', None)
    st.session_state.setdefault('na_count', 0)
    st.session_state.setdefault('resume_path', None)

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
        if resume_text:  # Only proceed if text extraction is successful
            st.session_state.parsed_data = resume_details(resume_text)
            st.session_state.na_count = count_na(st.session_state.parsed_data)[0]
            if not save_resume_analysis(st.session_state.email, st.session_state.parsed_data):
                st.error("Failed to save resume data to database.")
        else:
            st.error("Failed to extract text from the uploaded PDF.")
    col1, col2, col3 = st.columns([1.4, 0.002, 1.4])
    with col1:
        st.markdown(
            '''<div style='margin-top:5rem;margin-bottom:-30px; text-align: center;'>
                <h5 style='color: #1d3557;'>Upload Your Resume</h5>
            </div>''',
            unsafe_allow_html=True
        )
        # Disable file uploader if subscription/trial has expired
        if (subscription_type == 'free' and current_time > trial_end) or (subscription_type == 'premium' and current_time > sub_end):
            st.warning("🔒 Please upgrade to premium to access the file uploader.")
        else:
            file_uploaded = st.file_uploader(" ", type=["pdf", "docx"], key="home_file_uploader")
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
                st.session_state.parsed_data = None
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
            'resume_score': resume_score(parsed_data),
            'Recommended_Additional_Skills': parsed_data.get("Recommended_Additional_Skills", [])
        }
        display_tips(tips_data, missing_fields=na_paths)
    
    display_footer()