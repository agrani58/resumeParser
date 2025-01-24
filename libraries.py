import streamlit as st
import base64, random 
import time,datetime
import mysql.connector
import nltk
import os
from io import BytesIO
from fpdf import FPDF
nltk.download('stopwords')
import google.generativeai as genai
#importing database
# from connection import db_connection
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
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage

import io,random
from Courses import ds_course, web_course,android_course, ios_course, uiux_course
from PIL import Image

from langchain_ollama import OllamaLLM  # New import