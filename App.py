
from libraries import *


#e63946 red , yellow #f1faee, blue #a8dadc, bluedark #457b9d, darkest blue #1d3557
#importing the html components
components()


# Directory where resumes will be stored
save_dir = './Uploaded_Resumes'

# Ensure the directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# display the resume
def show_resume(resume_path, resume_type):
    
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
    with open(resume_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

# ATS only accepts text based pdf and rejects scanned image pdf
def is_text_based_pdf(resume_path):
    with pdfplumber.open(resume_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                return True
        return False

#allowed fonts (Arial, Calibri, Helvetica, Georgia, Times New Roman)
def check_fonts(resume_path):
    doc = fitz.open(resume_path)
    allowed_fonts = ["Arial", "Calibri", "Helvetica", "Georgia", "Times New Roman"]
    for page in doc:
        for font in page.get_fonts(full=True):
            font_name = font[0]  
            if isinstance(font_name, str):
                if not any(allowed_font in font_name for allowed_font in allowed_fonts):
                    return False  # If a disallowed font is found
            else:
                # Handle cases where font_name is not a string (e.g., logging or skipping)
                print(f"Non-string font name encountered: {font_name}")
    return True  

# Check for essential sections in the resume (work experience, education, skills, summary)
def check_structure(resume_path):
    headings = ["work experience", "education", "skills", "summary"]
    with pdfplumber.open(resume_path) as pdf:
        text = " ".join(page.extract_text() for page in pdf.pages if page.extract_text())
    st.write(text)
    return all(re.search(fr"\b{heading}\b", text, re.IGNORECASE) for heading in headings)


def resume_reader(resume_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()  # Virtual file in memory to store extracted text temporarily
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    
    with open(resume_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    
    converter.close()
    fake_file_handle.close()
    return text

def check_ats_compatibility(save_resume_path):
    # Check if the resume is text-based
    if not is_text_based_pdf(save_resume_path):
        st.error("Error: The PDF is not text-based, and may not be ATS-compatible.")
        return

    # Check if the fonts used in the resume are ATS-friendly
    if not check_fonts(save_resume_path):
        st.error("Error: The fonts used in the resume are not ATS-friendly.")
        return

    # Check if the required sections (headings) are present in the resume
    if not check_structure(save_resume_path):
        st.error("Error: Required sections (Work Experience, Education, Skills, Summary) are missing.")
        return

    # If all checks pass
    st.success("Success: The resume passes the ATS test.")



# File uploading box
file_uploaded = st.file_uploader(" ", type=["pdf", "DOCX"])

# Check if the file is uploaded
if file_uploaded is not None:
    
    file_extension = file_uploaded.name.split('.')[-1].lower()
# Save the uploaded file to the specified directory
    save_resume_path = os.path.join(save_dir, file_uploaded.name)
    
    if file_extension not in ["pdf", "docx"]:
        st.error("Unsupported file type. Please upload a PDF or DOCX file.")
    else:
        placeholder = st.empty()
        with st.spinner('Uploading your resume...'):
            time.sleep(1)  # Time between loading the file and displaying the file
        save_resume_path = os.path.join(save_dir, file_uploaded.name)
        
        with open(save_resume_path, "wb") as f:
            f.write(file_uploaded.getbuffer())
        show_resume(save_resume_path, file_extension)
        placeholder.success("Resume uploaded successfully!")
        time.sleep(4)
        placeholder.empty()
        
        #save all resume in save_dir wich points to Uploaded_resume
        save_resume_path = './Uploaded_Resumes/' + file_uploaded.name
        with open(save_resume_path, "wb") as f:
            f.write(file_uploaded.getbuffer())
    
    check_ats_compatibility(save_resume_path)
    resume_data = ResumeParser(save_resume_path).get_extracted_data()
    if resume_data:
        resume_text=resume_reader(save_resume_path)
        st.markdown('''<div style='margin-top: 40px; margin-left: 265px; margin-bottom: 20px'> <h4 style='color:#1d3557;'>Resume Analysis</h4>
            </div>''', unsafe_allow_html=True)
        
        st.markdown(f"Hello **{resume_data['name']}**!")

        st.markdown('''<div style='margin-top: 20px; margin-left:0px; margin-bottom:5px'> <h5 style='color:#1d3557;'>Basic User Info</h5>
                </div>''', unsafe_allow_html=True)

        st.text('Name: '+resume_data['name'])
        st.text('Email: ' + resume_data['email'])
        st.text('Contact: ' + resume_data['mobile_number'])
        # Safely get the 'mobile_number' or display 'Not available' if the value is None or the key doesn't exist
        mobile_number = resume_data.get('mobile_number', 'Not available')

# Ensure it's treated as a string for concatenation
    st.text('Contact: ' + str(mobile_number))

    st.text('Resume pages: '+str(resume_data['no_of_pages']))

    # except:
    #     pass
    #     candidate_level =''
    #     if resume_data['no_of_pages'] == 1:
    #         candidate_level = "Fresher"
    #         st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
    #     elif resume_data['no_of_pages'] == 2:
    #         candidate_level = "Intermediate"
    #         st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
    #     elif resume_data['no_of_pages'] >=3:
    #         candidate_level = "Experienced"
    #         st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)






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

# st.subheader("**Skills Recommendation💡**")
                ## Skill shows
    keywords = st_tags(label='### Your Current Skills',
        text='See our skills recommendation below',
        value=resume_data['skills'],key = '1  ')

##  keywords
