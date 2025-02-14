import streamlit as st
import base64, random 
import time,datetime

import nltk
import os
from io import BytesIO
from fpdf import FPDF
nltk.download('stopwords')
import google.generativeai as genai
#importing database
# from connection import db_connection
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
from PIL import Image


# Add these required imports
import mysql.connector
import streamlit_authenticator as stauth