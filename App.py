import streamlit as st
import base64, random 
import time,datetime
#importing database
from connection import db_connection
#libraries for parsing 

from pyresparser import ResumeParser
from pdfminer3.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer3.layout import LAParams,LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.converter import TextConverter
import io,random
from Courses import ds_course, web_course,android_course, ios_course, uiux_course
from PIL import Image
import pymysql
import pafy

import nltk
nltk.download('stopwords')



def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_filed, cand_level, skills, recommended_skills, courses):
        DB_table_name = 'user_data'
        insert_sql = f"""
        INSERT INTO {DB_table_name}
        VALUES (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        rec_values = (
            name, email, str(res_score), timestamp, str(no_of_pages), 
            reco_filed, cand_level, skills, recommended_skills, courses)
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

        #database part completed.
#page title and logo 
st.set_page_config(
    page_title="Resume Parser",
    page_icon="resumelogo.jpg",
)

def run():
    img= Image.open('./logo.png')
    img=img.resize((250,250))
    st.image(img,caption="Logo")
