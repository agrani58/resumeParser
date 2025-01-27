
from libraries import *
import streamlit_authenticator as stauth
from PyPDF2 import PdfReader
from json_file import resume_details, display_parsed_data, count_na  # Add count_na here
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos

uploaded_resume_dir = os.path.abspath('./Uploaded_Resumes')
    # docx_resume_path = os.path.abspath('./Uploaded_docx_resume') # The path of the uploaded file (DOCX or PDF)
    # Ensure the directory exists
if not os.path.exists(uploaded_resume_dir):
        os.makedirs(uploaded_resume_dir)

    # Function to display the resume PDF
def show_resume(uploaded_resume_path):
    try:
        with open(uploaded_resume_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying resume: {e}")
        
        
def extract_text_from_pdf(uploaded_resume_path):
    try:
        with open(uploaded_resume_path, "rb") as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() 
                #get resume details from model
            response=resume_details(text)
            return response
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None
def course_recommender(course_list):
    st.subheader("Courses and  Certificates Recommendation")
    c=0 
    rec_course=[]
    no_of_reco=st.slider("choose no of courses you want to be recommended:", 1,5,10)
    random.shuffle(course_list)
    for c_name,c_link in course_list:
        c+=1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c==no_of_reco:
            break
        
        return rec_course

def run():
    
    components()

        
    def convert_docx_to_pdf(docx_resume_path):
        
        if docx_resume_path.endswith(".docx"): 
            try:
                # Initialize COM threading model
                pythoncom.CoInitialize()  # COM allows different software components (written in different languages) to communicate with each other.

                # Define paths for DOCX and the output PDF
                uploaded_resume_path = os.path.splitext(docx_resume_path)[0] + ".pdf"  

                # Initialize Word COM object
                word = comtypes.client.CreateObject("Word.Application")
                word.Visible = False  # Run Word in the background

                # Open DOCX and save as PDF
                in_file = word.Documents.Open(docx_resume_path)
                in_file.SaveAs(uploaded_resume_path, FileFormat=17)  # PDF format constant
                in_file.Close()
                word.Quit()

            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
                return None
            finally:
                # Uninitialize COM after usage
                pythoncom.CoUninitialize()

        return uploaded_resume_path  # Return the path to the converted PDF file

    st.markdown(
            '''<div style='margin-top: 20px; text-align: center;'>
                <h5 style='color: #1d3557;'>Upload your Resume</h5>
            </div>''',
            unsafe_allow_html=True
        )

    # Initialize session state
    if 'prev_upload' not in st.session_state:
        st.session_state.update({
            'prev_upload': None,
            'parsed_data': None,
            'na_count': 0
        })

    file_uploaded = st.file_uploader(" ", type=["pdf", "docx"])
    
    # Detect new upload and reset state
    if file_uploaded != st.session_state.prev_upload:
        st.session_state.prev_upload = file_uploaded
        st.session_state.parsed_data = None
        st.session_state.na_count = 0
        st.rerun()  # Clear previous outputs

        
    if file_uploaded is not None:
        # Save the uploaded file to the appropriate directory
        file_extension = file_uploaded.name.split('.')[-1].lower()
        placeholder = st.empty()
        # Determine the path for the file
        uploaded_resume_path = os.path.join(uploaded_resume_dir, file_uploaded.name)
            # Save the PDF directly
        with open(uploaded_resume_path, "wb") as f:
            f.write(file_uploaded.getbuffer())
            
        if file_extension == "pdf":
            placeholder.success("Resume uploaded successfully!")
            time.sleep(4)
            placeholder.empty()
            show_resume(uploaded_resume_path)
        elif file_extension == "docx":
            # Save the DOCX file temporarily, convert it to PDF, and save the PDF
            converted_pdf_path = convert_docx_to_pdf(uploaded_resume_path)
            if converted_pdf_path:
                uploaded_resume_path = converted_pdf_path  # Update the path to the converted PDF
                st.success("DOCX converted to PDF successfully!")
            show_resume(uploaded_resume_path)
        else:
                st.error("DOCX conversion failed.") 
                

        with st.spinner("Extracting and parsing resume..."):
            resume_text = extract_text_from_pdf(uploaded_resume_path)
            if resume_text:
                st.session_state.parsed_data = resume_details(resume_text)
        if st.session_state.parsed_data:
            display_parsed_data(st.session_state.parsed_data)
            
        na_count, na_paths = count_na(st.session_state.parsed_data)
        
        if na_count > 0:
        # Group missing fields by category
            category_groups = {}
        for path in na_paths:
            # Remove array indexes and split into components
            clean_path = path.replace("[0]", "").replace("_", " ").title()
            parts = clean_path.split('.')
            
            # Group by parent category
            if len(parts) > 1:
                category = parts[0]
                field = parts[1]
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(field)
            else:
                category_groups[clean_path] = None

        # Create display items
        display_items = []
        for category, fields in category_groups.items():
            if fields:
                display_items.append(f"{category}: {', '.join(fields)} Missing")
            else:
                display_items.append(category)

        st.markdown(f"""
        <div style="margin-top: 20px; padding: 10px; background-color: #ffe6e6; border-radius: 5px;">
            ⚠️ Found {na_count} missing fields:
            <ul style="margin: 8px 0;">
                {"".join([f"<li>{item}</li>" for item in display_items])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

#         # Call the run function to execute the app
if __name__ == "__main__":
        run()


