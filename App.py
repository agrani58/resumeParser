import streamlit as st
import base64, random 
import time,datetime
import pymysql
import pafy
import nltk
nltk.download('stopwords')
#importing database
from connection import db_connection
#libraries for parsing from datetime import datetime 
from pyresparser import ResumeParser
from pdfminer3.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer3.layout import LAParams,LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.converter import TextConverter
import io,random
from Courses import ds_course, web_course,android_course, ios_course, uiux_course
from PIL import Image


#e63946 red , yellow #f1faee, blue #a8dadc, bluedark #457b9d, darkest blue #1d3557

st.set_page_config(
    page_title="Resume Parser",
    page_icon='Logo\logo.png',
)

# page background colors
page_bg_color ="""
<style>
.stApp {
    background-color: #f0f8ff; /* Light blue color */
}
</style>"""
st.markdown(page_bg_color, unsafe_allow_html=True)

sidebar_bg_color= """
<style>
    .css-1d391kg { 
    background-color: #E5ECE9; 
}
</style>"""
st.markdown(sidebar_bg_color , unsafe_allow_html=True)
#back ground color ends

st.sidebar.markdown("Choose user")
activities=["User","Admin"]
choice = st.sidebar.selectbox("Choose among the given options:",activities)

def run():

    try:
        # Displaying the image in the center using st.image
        col1, col2, col3 = st.columns([1, 2, 1])  # Create 3 columns for alignment
        with col2:  # Place the image in the middle column
            
            st.markdown("<style>img {margin-top: -50px; margin-left: -75px }</style>", unsafe_allow_html=True) #img represents all images so it brings all img to -50 
            st.image("Logo/logo2.png",caption="           ", width=500)  
            st.markdown("<div style ='margin-top: -30px; margin-left:110px;'> <p>AI Resume Parser</p></div>", unsafe_allow_html=True)


    except FileNotFoundError:
        st.error("Image file not found!")


# Run the app
if __name__ == "__main__":
    run()
    
if choice == 'User':
    st.markdown('''<div style='margin-top: 20px; margin-left: 265px; margin-bottom: -40px'> <h5 style='color:#1d3557;'>Upload your Resume</h5>
    </div>''', unsafe_allow_html=True)


    
#file uploading box.
file_uploader=st.file_uploader("",type=["pdf","DOCX"])
if file_uploader is not None:
    with st.spinner('uploading your resume...'):
        time.sleep(5)
    save_image_path ='./Uploaded_Resume/'+file_uploader.name
    
    
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


