from libraries import *
from ats import convert_docx_to_pdf
import streamlit_authenticator as stauth
from PyPDF2 import PdfReader

from collections import defaultdict 
# In home.py - Update import statement
from json_file import resume_details, display_parsed_data, count_na 
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
            na_count, na_paths = count_na(st.session_state.parsed_data)
            display_parsed_data(st.session_state.parsed_data, missing_fields=na_paths)
            # Remove the old missing fields summary code here
            
        na_count, na_paths = count_na(st.session_state.parsed_data)
                        
        # In display_parsed_data() function
        clean_paths = [
            re.sub(r'\[\d+\]', '', p)  # Remove array indices
            .title()  # Remove .replace("_", " ")
            for p in na_paths
        ]

                # Group by parent category
        field_counts = defaultdict(int)
        category_fields = defaultdict(set)
        standalone_fields = set()

        for path in clean_paths:
            if '.' in path:
                category, field = path.split('.', 1)
                category_fields[category].add(field)
                field_counts[f"{category}.{field}"] += 1
            else:
                standalone_fields.add(path)
                field_counts[path] += 1
        st.markdown(
            '''<div style='margin-top: 20px; text-align: center;'>
                <h5 style='color: #1d3557;'>Resume Tips & Tricks</h5>
            </div>''',
            unsafe_allow_html=True
        )

        # In home.py, after counting NA
        st.markdown(f"""
            <div style="margin-top: 20px; padding: 10px; background-color: #ffe6e6; border-radius: 25px; text-align: center;">
                ⚠️ Found {na_count} missing fields. Include this field to make your resume ATS compatible.
            </div>
        """, unsafe_allow_html=True)

#         # Call the run function to execute the app
if __name__ == "__main__":
        run()