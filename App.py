from libraries import *

#e63946 red , yellow #f1faee, blue #a8dadc, bluedark #457b9d, darkest blue #1d3557
#importing the html components
components()


# #Convert .docx to PDF:
# import pypandoc
# def docx_to_pdf(docx_path, pdf_path):
#     # Convert the .docx file to a PDF
#     output = pypandoc.convert_docx(docx_path, 'pdf', outputfile=pdf_path)
#     return output

# # Usage
# docx_path = "path_to_your_resume.docx"
# pdf_path = "converted_resume.pdf"
# docx_to_pdf(docx_path, pdf_path)
# print(f"PDF saved at {pdf_path}")

# display the resume
def show_resume(resume_path,resume_type):
    if resume_type =="pdf":
        with open(resume_path, "rb") as f:
            base64_pdf= base64.b64encode(f.read()).decode('utf-8')
        pdf_display=F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display,unsafe_allow_html=True);
        
    elif resume_type == "docx":
        pdf_data = docx_to_pdf(resume_path)
        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.error("Unsupported file type. Please upload a PDF or DOCX file.")
             
def resume_reader(file):
    resource_manager=PDFResourceManager()#identify and manage pdf fonts
    fake_file_handle =io.StringIO() #virtual file in memeoryy to store extracted text temporiraly 
    converter = TextConverter(resource_manager,fake_file_handle,laparams=LAParams())
    page_interpretor=PDFPageInterpreter(resource_manager,converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,caching=True,check_extractable=True):
            page_interpretor.process_page(page)
            print(page)
        text=fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

# Directory where resumes will be stored
save_dir = './Uploaded_Resumes'

# Ensure the directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

#file uploading box.
file_uploaded=st.file_uploader(" ",type=["pdf","DOCX"])
if file_uploaded is not None:
    with st.spinner('uploading your resume...'):
        time.sleep(2) #time between loading the file and displaying the file
    save_resume_path =os.path.join(save_dir ,file_uploaded.name)
    resume_type = save_resume_path.split('.')[-1] #extracts file type
#read file in binary   
    with open(save_resume_path,"wb") as f: 
        f.write(file_uploaded.getbuffer())
        
    show_resume(save_resume_path, resume_type)
    resume_data=ResumeParser(save_resume_path).get_extracted_data()
    
    
    #display the resume
    if resume_data:
        resume_text = " ".join([str(value) for value in resume_data.values()])  # Combine the extracted data into a single string
        st.text_area("Extracted text here", resume_text, height=1000)

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



def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title


