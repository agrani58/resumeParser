import streamlit as st
import base64, random 
import time,datetime
import pymysql
import nltk
import os
from io import BytesIO
from fpdf import FPDF
nltk.download('stopwords')
#importing database
from connection import db_connection
from components import components
#libraries for parsing from datetime import datetime 
#word to pdf
import docx
from docx import Document
import comtypes.client
import pythoncom

#ATS compatibility
import pdfplumber
import fitz #PyMuPDF for fonts
import re
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.high_level import extract_text

import io,random
from Courses import ds_course, web_course,android_course, ios_course, uiux_course
from PIL import Image