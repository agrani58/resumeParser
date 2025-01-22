
from libraries import *
from langchain_community.llms import Ollama
from json_helper import InputData as input  # Make sure InputData is correctly imported
from pdfminer.high_level import extract_text
from clean_text import clean_text

from pathlib import Path
import streamlit_authenticator as stauth

from model import extract_text_from_pdf, process_resume_with_model
#e63946 red , yellow #f1faee, blue #a8dadc, bluedark #457b9d, darkest blue #1d3557
#importing the html components
def run():
    components()

    # Directory where resumes will be stored
    uploaded_resume_dir = './Uploaded_Resumes'

    # Ensure the directory exists
    if not os.path.exists(uploaded_resume_dir):
        os.makedirs(uploaded_resume_dir)

        # Display the PDF
    st.markdown(
    '''<div style='margin-top: 20px; text-align: center;'>
        <h5 style='color: #1d3557;'>Upload your Resume</h5>
    </div>''',
    unsafe_allow_html=True
)

#-- USER AUTHENTICATION---
    #-- USER AUTHENTICATION CLOSE-----

    def show_resume(resume_path, resume_type):
            with open(resume_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)      
        # ATS only accepts text based pdf and rejects scanned image pdf

        # display the resume
    def convert_docx_to_pdf(resume_path, resume_type):
            save_dir = resume_path  # Initialize save_dir as resume_path (in case it's already a PDF)
            if resume_type != "pdf":
                try:
                    # Initialize COM threading model
                    pythoncom.CoInitialize() # COM allows different software components (written in different languages) to communicate with each other.

                    # Define paths for DOCX and the output PDF
                    docx_path = os.path.abspath(resume_path)
                    save_dir = os.path.splitext(docx_path)[0] + ".pdf"  # Replace .docx with .pdf

                    # Initialize Word COM object
                    word = comtypes.client.CreateObject("Word.Application")
                    word.Visible = False  # Run Word in the background

                    # Open DOCX and save as PDF
                    in_file = word.Documents.Open(docx_path)
                    in_file.SaveAs(save_dir, FileFormat=17)  # PDF format constant
                    in_file.Close()
                    word.Quit()
                    
                except Exception as e:
                    st.error(f"An error occurred during conversion: {e}")
                    return
                finally:
                #uninitialize COM after usage
                    pythoncom.CoUninitialize()
            return save_dir  # Return the path to the converted PDF file


    def resume_reader(save_dir):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()  # Virtual file in memory to store extracted text temporarily
            laparams = LAParams()
            converter = TextConverter(resource_manager, fake_file_handle, laparams=laparams)
    
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            
            with open(save_dir, 'rb') as fh:
                for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                    page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()
            
            converter.close()
            fake_file_handle.close()
            return text

        # File uploaded by the user
    file_uploaded = st.file_uploader("     ", type=["pdf", "docx"])

        # Check if the file is uploaded
    if file_uploaded is not None:
            file_extension = file_uploaded.name.split('.')[-1].lower()

            if file_extension not in ["pdf", "docx"]:
                st.error("Unsupported file type. Please upload a PDF or DOCX file.")
            else:
                placeholder = st.empty()
                with st.spinner('Uploading your resume...'):
                    time.sleep(1)  # Time between loading the file and displaying it
                save_dir = os.path.join(uploaded_resume_dir, file_uploaded.name)  # Path where the file will be saved
                
                # Save the uploaded file to the directory
                with open(save_dir, "wb") as f:
                    f.write(file_uploaded.getbuffer())
                
                # Display the uploaded resume
                show_resume(save_dir, file_extension)
                placeholder.success("Resume uploaded successfully!")
                time.sleep(4)
                placeholder.empty()
                
                # Extract text from the file (PDF or the converted DOCX to PDF)
            # Extract text from the file (PDF or the converted DOCX to PDF)
                resume_text = extract_text_from_pdf(save_dir)

                # Clean the extracted resume text using clean_text function
                cleaned_resume_text = clean_text(resume_text)  # Fixed variable name

                # If resume text was extracted and cleaned, process it using the model
                if cleaned_resume_text:  # Check if the cleaned resume text is not empty
                    parsed_result = process_resume_with_model(cleaned_resume_text)  # Pass the cleaned text to the model
                
                # Display cleaned text
                st.subheader("Cleaned Resume Text:")
                st.write(cleaned_resume_text)  # Display the cleaned text

                # Display parsed result
                if parsed_result:
                    st.subheader("Extracted Information:")
                    st.json(parsed_result)  # Display the parsed result as JSON
                else:
                    st.error("Error processing resume with the model.")
        #database insertion starts 
        # def insert_data(name, email, resume_score, timestamp, no_of_pages, recommendation_field, candidate_level, skills, recommended_skills, courses):
        #         DB_table_name = 'user_data'
        #         insert_sql = f"""
        #         INSERT INTO {DB_table_name}
        #         VALUES (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        #         """
        #         rec_values = (
        #             name, email, str(resume_score), timestamp, str(no_of_pages), recommendation_field, candidate_level, skills, recommended_skills, courses)
        #     #connect to the database

        #         conn = db_connection()
        #         if conn:
        #             try:
        #                 cursor = conn.cursor()
        #                 cursor.execute(insert_sql,rec_values)
        #                 conn.commit()
        #                 print("Data inserted successfully.")
        #             except pymysql.MySQLError as e:
        #                 print(f"Error during data insertion: {e}")
        #             finally:
        #                 cursor.close()
        #                 conn.close()
        #         else:
        #             print("Database connection failed. data not inserted.")
                #database connection completed
                
        # DB_table_name = 'user_data'
        # table_sql = """CREATE TABLE IF NOT EXISTS """ + DB_table_name + """ (
        #                                 ID INT AUTO_INCREMENT,
        #                                 Name VARCHAR(50) NOT NULL,
        #                                 Email_ID VARCHAR(50) NOT NULL,
        #                                 Resume_score VARCHAR(8) NOT NULL,
        #                                 Timestamp VARCHAR(50) NOT NULL,
        #                                 Page_no VARCHAR(5) NOT NULL,
        #                                 Predicted_field BLOB NOT NULL,
        #                                 User_level BLOB NOT NULL,
        #                                 Actual_skills BLOB NOT NULL,
        #                                 Recommended_skills BLOB NOT NULL,
        #                                 Recommended_courses BLOB NOT NULL,
        #                                 PRIMARY KEY (ID)
        #                             );
        #                             """
                #testing database with input value 
        # def test_insert_data():
        #     name = "John Doe" 
        #     email = "johndoe@example.com"
        #     resume_score = 85.5
        #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     no_of_pages = 2
        #     recommendation_field = "Improve soft skills"
        #     candidate_level = "Intermediate"
        #     skills = "Python, SQL, Excel"
        #     recommended_skills = "Machine Learning, Power BI"
        #     courses = "Data Science Bootcamp, Business Analytics"
        #     insert_data(name, email, resume_score, timestamp, no_of_pages, recommendation_field, candidate_level, skills, recommended_skills, courses)
                
        # test_insert_data()


