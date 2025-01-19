
from libraries import *


#e63946 red , yellow #f1faee, blue #a8dadc, bluedark #457b9d, darkest blue #1d3557
#importing the html components
components()


# Directory where resumes will be stored
uploaded_resume_dir = './Uploaded_Resumes'

# Ensure the directory exists
if not os.path.exists(uploaded_resume_dir):
    os.makedirs(uploaded_resume_dir)

# display the resume
def convert_docx_to_pdf(resume_path, resume_type):
    
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
            
            resume_path = save_dir
            resume_type = "pdf"
        except Exception as e:
            st.error(f"An error occurred during conversion: {e}")
            return
        finally:
        #uninitialize COM after usage
            pythoncom.CoUninitialize()

    # Display the PDF
def show_resume(resume_path, resume_type):
    with open(resume_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

# ATS only accepts text based pdf and rejects scanned image pdf
def extract_text_from_pdf(save_dir):
    with pdfplumber.open(save_dir) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def resume_reader(save_dir):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()  # Virtual file in memory to store extracted text temporarily
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    
    with open(save_dir, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    
    converter.close()
    fake_file_handle.close()
    return text



# File uploading box
file_uploaded = st.file_uploader(" ", type=["pdf", "DOCX"])

# Check if the file is uploaded
if file_uploaded is not None:
    
    file_extension = file_uploaded.name.split('.')[-1].lower()

    if file_extension not in ["pdf", "docx"]:
        st.error("Unsupported file type. Please upload a PDF or DOCX file.")
    else:
        placeholder = st.empty()
        with st.spinner('Uploading your resume...'):
            time.sleep(1)  # Time between loading the file and displaying the file
        save_dir = os.path.join(uploaded_resume_dir, file_uploaded.name)
        
        with open(save_dir, "wb") as f:
            f.write(file_uploaded.getbuffer())
        show_resume(save_dir, file_extension)
        placeholder.success("Resume uploaded successfully!")
        time.sleep(4)
        placeholder.empty()
        
        #save all resume in save_dir wich points to Uploaded_resume
        save_dir = './Uploaded_Resumes/' + file_uploaded.name
        with open(save_dir, "wb") as f:
            f.write(file_uploaded.getbuffer())
    
 # If the file is DOCX, convert it to PDF
        if file_extension == "docx":
            save_dir = convert_docx_to_pdf(save_dir, file_extension) 
        
        # Now you can extract text from the PDF file
        if save_dir.endswith(".pdf"):
            resume_text = extract_text_from_pdf(save_dir)
            # Use the resume_text for further processing
            st.text(resume_text)

#database insertion starts 
def insert_data(name, email, resume_score, timestamp, no_of_pages, recommendation_field, candidate_level, skills, recommended_skills, courses):
        DB_table_name = 'user_data'
        insert_sql = f"""
        INSERT INTO {DB_table_name}
        VALUES (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        rec_values = (
            name, email, str(resume_score), timestamp, str(no_of_pages), recommendation_field, candidate_level, skills, recommended_skills, courses)
    #connect to the database

        conn = db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(insert_sql,rec_values)
                conn.commit()
                print("Data inserted successfully.")
            except pymysql.MySQLError as e:
                print(f"Error during data insertion: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            print("Database connection failed. data not inserted.")
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


