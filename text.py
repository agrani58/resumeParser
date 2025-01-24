
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import streamlit as st
import requests

load_dotenv()
# Load environment variables from the .env file
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# Define the API endpoint and API key (if required)
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def resume_details(resume):
    prompt=f"""
    You are a resume parsing assistant. Given the following resume text, extract all the important details are return them in a well-structured JSON format. 
    the reusme text:
    {resume}
    Extract and include the following:
    -Name
    -Email
    -Phone_1
    -Phone_2
    -Address
    -City 
    -Linkedin
    -Github
    -Professional_Experience_in_Years
    -Highest_Education
    -Skills
    -Applied_for_Profile
    -Education
    -Professional_Experience 
    -Certifications
    -Suggested Resume Category (based on skills and Experience)
    -Recommended Additional Skills(based on candidate's skills and experience)
    
    Return Response in JSON format
    """
        
    response= model.generate_content(prompt).text
    response_clean = response.replace("```json", "").replace("```", "").strip()
    try:
            # Parse response as JSON
        data = json.loads(response_clean)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


def display_parsed_data(data):
    if not data:
        st.error("Error: No valid resume data to display")
        return
    
    st.header("**Resume Analysis**")
        # Extract parsed data fields
    Full_Name = data.get("Name", "")
    Email = data.get("Email", "")
    Contacts = f"Contact:\nPhone 1: {data.get('Phone_1', 'N/A')}\nPhone 2: {data.get('Phone_2', 'N/A')}"
    Address = data.get("Address", "")
    City = data.get("City", "")
    Linkedin = data.get("Linkedin", "")
    Github = data.get("Github", "")
    Applied_for_Profile = data.get("Applied_for_Profile", "")
    Professional_Experience_in_Years = data.get("Professional_Experience_in_Years", "")
    Highest_Education = data.get("Highest_Education", "")
    Skills = ", ".join(data.get("Skills", []))
    Education = data.get("Education", [])
    Education_str = " ".join([
    f"{edu.get('Degree', ' ')} from {edu.get('University', ' ')} (Graduated: {edu.get('Graduation Date', ' ')})"
        for edu in Education  ])
    Professional_Experience = data.get("Professional_Experience", [])
    Professional_Experience_str = "\n".join([f"{job.get('Job Title', '')} from {job.get('Company', '')} ({job.get('Years of Experience', '')})"
        for job in Professional_Experience])
    Certifications = ", ".join(data.get("Certifications", []))
    Suggested_Resume_Category = data.get("Suggested_Resume_Category", "")
    Recommended_Additional_Skills = data.get("Recommended_Additional_Skills", "")

    st.write(f"**Name:** {Full_Name}")
    st.write(f"**Email:** {Email}")
    st.write(f"**Contacts:** {Contacts}")
    st.write(f"**Address:** {Address}")
    st.write(f"**City:** {City}")
    st.write(f"**Linkedin:** {Linkedin}")
    st.write(f"**Github:** {Github}")
    st.write(f"**Profile Applied For:** {Applied_for_Profile}")
    st.write(f"**Experience in Years:** {Professional_Experience_in_Years}")
    st.write(f"**Highest Education:** {Highest_Education}")
    st.write(f"**Skills:** {Skills}")
    st.write(f"**Education Details:** {Education_str}")
    st.write(f"**Professional Experience:** {Professional_Experience_str}")
    st.write(f"**Certifications:** {Certifications}")
    st.write(f"**Resume Category:** {Suggested_Resume_Category}")
    st.write(f"**Recommended Additional Skills:** {Recommended_Additional_Skills}")

