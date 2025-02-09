from PyPDF2 import PdfReader



from app.libraries import *
import app.accounts as accounts
from app.config import cookie_controller
from app.utils import count_na, is_valid_date, resume_details, resume_score
from app.schema import create_connection, delete_session_token, save_resume_analysis
from app.view import display_footer, display_parsed_data, display_tips

def get_user_upload_dir():
    """Get the user-specific upload directory."""
    if not st.session_state.get('authenticated'):
        return None
    return os.path.join('./Uploaded_Resumes', st.session_state.email)

def convert_docx_to_pdf(docx_resume_path):
    if docx_resume_path.endswith(".docx"): 
        try:
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
    """Display the uploaded resume PDF."""
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
    """Clear uploaded files on logout."""
    user_dir = get_user_upload_dir()
    if user_dir and os.path.exists(user_dir):
        for f in os.listdir(user_dir):
            os.remove(os.path.join(user_dir, f))
        os.rmdir(user_dir)

def run():
    from app import admin
    if st.session_state.authenticated and st.session_state.role_id == 2:
        admin.run()
        st.stop()
    components()
    parsed_data = {}
    
    st.session_state.setdefault('uploaded_file', None)
    st.session_state.setdefault('parsed_data', None)
    st.session_state.setdefault('na_count', 0)
    st.session_state.setdefault('resume_path', None)

    accounts.check_session() 
    if not st.session_state.get('authenticated'):
        st.warning("Please login first!")
        run()
        return

    user_dir = get_user_upload_dir()
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    if st.sidebar.button("Logout"):
        clear_user_files()
        keys_to_remove = ['uploaded_file', 'parsed_data', 'na_count', 'resume_path', 'parsed_resume', 'analysis_done', 'file_processed']
        for key in keys_to_remove:
            st.session_state.pop(key, None)
        session_token = cookie_controller.get("session_token")
        if session_token:
            delete_session_token(session_token)
            cookie_controller.set("session_token", "", max_age=0)
        st.session_state.authenticated = False
        st.session_state.pop("email", None)
        st.rerun()

    if not st.session_state.resume_path:
        existing_files = [f for f in os.listdir(user_dir) if f.lower().endswith(('.pdf', '.docx'))]
        if existing_files:
            latest_file = max(existing_files, key=lambda x: os.path.getmtime(os.path.join(user_dir, x)))
            st.session_state.resume_path = os.path.join(user_dir, latest_file)

    if st.session_state.resume_path and not st.session_state.parsed_data:
        resume_text = extract_text_from_pdf(st.session_state.resume_path)
        if resume_text:
            st.session_state.parsed_data = resume_details(resume_text)
            st.session_state.na_count = count_na(st.session_state.parsed_data)[0]
            # Save parsed data to database
            if save_resume_analysis(st.session_state.email, st.session_state.parsed_data):
                st.success("Resume data saved to database!")
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
        file_uploaded = st.file_uploader(" ", type=["pdf", "docx"], key="persistent_uploader")
        placeholder = st.empty()

        if file_uploaded and (file_uploaded != st.session_state.uploaded_file):
            for f in os.listdir(user_dir):
                os.remove(os.path.join(user_dir, f))
            file_extension = file_uploaded.name.split('.')[-1].lower()
            uploaded_resume_path = os.path.join(user_dir, file_uploaded.name)
            with open(uploaded_resume_path, "wb") as f:
                f.write(file_uploaded.getbuffer())
            placeholder.success("Resume uploaded successfully!")
            time.sleep(2)
            
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

        if st.session_state.resume_path and os.path.exists(st.session_state.resume_path):
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
        display_tips(tips_data,missing_fields=na_paths)

    display_footer()    