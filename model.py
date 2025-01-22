import streamlit as st  # Import Streamlit
from pdfminer.high_level import extract_text
from json_helper import InputData as input  # Ensure this is correctly imported
from clean_text import clean_text  # Import the clean_text function

def extract_text_from_pdf(save_dir):

    return extract_text(save_dir)

def process_resume_with_model(cleaned_text):
   
    input_text = input.input_data(cleaned_text)  # Pass the cleaned text here
    
    # Initialize the Ollama model
    llm = input.llm()
    
    # Get the model response with the resume text
    data = llm.invoke(input_text)  # Get data from the model
    
    return data

