#Core utilities
import json
import random
import yt_dlp 
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
from app.schema import resume_videos,interview_videos
load_dotenv()

# Load environment variables from the .env file
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# Convert None to N/A recursively through nested structures
def convert_none(obj):
    if isinstance(obj, dict):
        return {k: convert_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_none(item) for item in obj]
    return obj if obj not in [None, "None"] else "N/A"
        
def count_na(parsed_data):
    missing_fields = [] 
    _tracker(parsed_data, missing_fields)
    return len(missing_fields), missing_fields 


def resume_details(resume_text):
    prompt = f"""
    You are a resume parsing assistant. Given the following resume text, extract the following details in a structured JSON format:

    - Name
    - Email
    - Phone_1
    - Address (Precise with city)
    - GitHub: extract patterns like github.com/username)"
    - LinkedIn: extract patterns linkedin.com/in/ patterns)"
    - Professional_Experience_in_Years
    - Highest_Education
    - Technical_Skills (list only technical/hard skills)
    - Soft_Skills (list only non-technical/soft skills)
    - Applied_for_Profile (given in the resume or education)
    - Education (Include EXACT field names):
        - University
        - Degree
        - Graduation_Date (use format 'Month YYYY')
    - Work_Experience (Include fields):
        - Job_Title
        - Company
        - Start_Date (use format 'Month YYYY')
        - End_Date (use format 'Month YYYY'or present)
        - Description
    - Projects: 
        - Project_Title
        - Description
    - Certifications
    - Achievements 
    - Suggested_Resume_Category (infer the most relevant job category based on skills, certifications, and work experience)
    - Recommended_Additional_Skills (provide 3-5 concrete skills relevant to the Suggested_Resume_Category)
    - Hobbies (list of interests /hobbies)
    The resume text:
    {resume_text}

    Return the information in a clean and readable JSON format. Ensure all fields are included. For Suggested_Resume_Category and Recommended_Additional_Skills, infer values if not explicitly stated—avoid 'N/A'.
    """
    response = model.generate_content(prompt).text
    response_api = response.replace("```json", "").replace("```", "").strip()
    json_match = re.search(r'\{.*\}', response_api, re.DOTALL)
    if json_match:
        response_api = json_match.group(0)
    else:
        raise ValueError("No JSON found in response")

    # Convert 'None' to 'N/A' in the response
    response_api = response_api.replace('"None"', '"N/A"').replace("'None'", "'N/A'")

    try:
        parsed_data = json.loads(response_api)
        required_top_level_fields = {
            "Name": "N/A",
            "Email": "N/A",
            "Phone_1": "N/A",
            "Address": "N/A",
            "LinkedIn": "N/A",
            "GitHub": "N/A",  
            "Professional_Experience_in_Years": "N/A",
            "Highest_Education": "N/A",
            "Technical_Skills": [],
            "Soft_Skills": [],
            "Applied_for_Profile": "N/A",
            "Certifications": [],
            "Suggested_Resume_Category": "N/A",
            "Achievements": [],
            "Hobbies": [],
            "Recommended_Additional_Skills": []
        }

        # Set defaults for missing fields
        for field, default in required_top_level_fields.items():
            parsed_data.setdefault(field, default)
            
        # Work Experience validation
        for job in parsed_data.get("Work_Experience", []):
            for field, default in [("Start_Date", "N/A"), ("End_Date", "N/A"), ("Description", [])]:
                job.setdefault(field, default)

        # Projects validation
        for project in parsed_data.get("Projects", []):
            for field, default in [("Project_Title", "N/A"), ("Description", [])]:
                project.setdefault(field, default)
                
        # Education validation
        for edu in parsed_data.get("Education", []):
            edu.setdefault("Graduation_Date", "N/A")
            if not is_valid_date(edu.get("Graduation_Date", "N/A")):
                edu["Graduation_Date"] = "N/A"
                
        # Certifications cleanup
        parsed_data["Certifications"] = [
            str(c).strip() for c in parsed_data.get("Certifications", [])
            if str(c).strip() not in ["N/A"]
        ]
        if not parsed_data["Certifications"]:
            parsed_data["Certifications"] = ["N/A"]
            
        parsed_data["Hobbies"] = [
        str(h).strip() for h in parsed_data.get("Hobbies", [])
        if str(h).strip() not in ["N/A", ""]
    ]
        # Convert remaining None values to N/A
        parsed_data = convert_none(parsed_data)
        return parsed_data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    
    
def _tracker(data, missing, path="", strict=False):
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            if isinstance(value, (dict, list)):
                _tracker(value, missing, new_path, strict)
            else:
                if key.lower() == "graduation_date" and not is_valid_date(str(value)):
                    missing.append(new_path)
                elif str(value).strip().upper() in ["N/A", "NA", "NONE", ""]:
                    missing.append(new_path)
        if not data and path:
            missing.append(path)
    elif isinstance(data, list):
        if not data and path:
            missing.append(path)
        for idx, item in enumerate(data):
            new_path = f"{path}[{idx}]" if path else f"[{idx}]"
            if isinstance(item, (dict, list)):
                _tracker(item, missing, new_path, strict)
            else:
                # Check if the item itself is "N/A"
                if str(item).strip().upper() in ["N/A", "NA", "NONE", ""]:
                    missing.append(new_path)
                    
def is_valid_date(date_str):
    """Check if date matches mm/yyyy or Month YYYY format"""
    if not isinstance(date_str, str):
        return False
    # Check for Month YYYY format (e.g., "May 2023")
    if len(date_str.split()) == 2:
        month, year = date_str.split()
        if month.lower() in ["january", "february", "march", "april", "may", "june",
                        "july", "august", "september", "october", "november", "december"]:
            return year.isdigit() and len(year) == 4
        
    # Check for mm/yyyy format (e.g., "05/2023")
    if len(date_str.split('/')) == 2:
        month, year = date_str.split('/')
        return month.isdigit() and 1 <= int(month) <= 12 and year.isdigit() and len(year) == 4
    
    if date_str in ["Present", "N/A"]:
        return True
    
def courses_recommendation(course_list):
            rec_course=[]
            if course_list:
                st.markdown("""<style> div[data-testid="stSlider"] > div { max-width: 80%; margin-top:-5px}</style>""", unsafe_allow_html=True)
                no_of_reco = st.slider('Choose Number of Courses You want to be Recommended.',1,5,3)
                random.shuffle(course_list)
                i = 1 
                for course in course_list[:no_of_reco]:
                    c_name, c_link = course  # Unpack the tuple
                    st.markdown(f'({i}) &nbsp;&nbsp;&nbsp;[{c_name}]({c_link})')
                    i += 1  # Increment the index
                    rec_course.append(c_name)
            return rec_course
        
def resume_score(parsed_data):
    resume_score = 0
    
    # Basic Contact Info (20 points)
    if parsed_data.get("LinkedIn", "N/A") != "N/A":
        resume_score += 5
    if parsed_data.get("GitHub", "N/A") != "N/A":
        resume_score += 5
    if parsed_data.get("Email", "N/A") != "N/A":
        resume_score += 5
    if parsed_data.get("Phone_1", "N/A") != "N/A":
        resume_score += 5

    # Core Sections (70 points)
    if parsed_data.get("Technical_Skills"):
        resume_score += 15
    if parsed_data.get("Soft_Skills"):
        resume_score += 15
    if parsed_data.get("Certifications"):  
        resume_score += 15
    if parsed_data.get("Achievements"):
        resume_score += 10
    if parsed_data.get("Projects"):
        resume_score += 15

    # Bonus Points (10 points)
    if parsed_data.get("Hobbies"):
        resume_score += 5
    if parsed_data.get("Work_Experience"):
        resume_score += 5

    return min(resume_score, 100)  # Ensure max 100

def fetch_yt_video():
    # Randomly select resume video
    resume_vid = random.choice(resume_videos)
    # Display with fixed aspect ratio
    st.markdown(f'''
        <div style="text-align:center;padding-top:1.5%;">
            <h5> ✅ Resume Writing Tips</h5>
        </div>
        <div style="position: relative; padding-bottom: 56.25%;">
            <iframe src="{resume_vid}" frameborder="1" allowfullscreen 
                style="position: absolute; left: 12rem; width: 70%; height: 70%;">
            </iframe>
            
        </div>
    ''', unsafe_allow_html=True)

    
    # Repeat for interview videos
    interview_vid = random.choice(interview_videos)

    
    st.markdown(f'''
        <div style="text-align:center;margin-top:-13.5%;">
            <h5> ✅ Interview Tips</h5>
        </div>
        <div style="position: relative; padding-bottom: 56.25%;">
            <iframe src="{interview_vid}" frameborder="1" allowfullscreen 
                style="position: absolute; left: 12rem; width: 70%; height: 70%;">
            </iframe>
        </div>
    ''', unsafe_allow_html=True)
    