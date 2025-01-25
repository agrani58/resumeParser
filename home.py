
from libraries import *
import streamlit_authenticator as stauth
from PyPDF2 import PdfReader
from json_file import resume_details, display_parsed_data
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos


    # Directory where resumes will be stored
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
    st.subheader("Courses and  Certificates Recommendation");
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
        
        if docx_resume_path.endswith(".docx"):  # Only convert DOCX files
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
    file_uploaded = st.file_uploader("       ", type=["pdf", "docx"])

    if file_uploaded is not None:
        # Save the uploaded file to the appropriate directory
        file_extension = file_uploaded.name.split('.')[-1].lower()

        # Determine the path for the file
        uploaded_resume_path = os.path.join(uploaded_resume_dir, file_uploaded.name)
            # Save the PDF directly
        with open(uploaded_resume_path, "wb") as f:
            f.write(file_uploaded.getbuffer())
            
        if file_extension == "pdf":
            st.success("Resume uploaded successfully!")
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
                parsed_data = resume_details(resume_text)
                if parsed_data:
                    display_parsed_data(parsed_data)

        course_recommender()



#         # Call the run function to execute the app
if __name__ == "__main__":
        run()


