import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import streamlit as st
from ats import is_valid_date,_tracker
load_dotenv()

# Load environment variables from the .env file
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def resume_details(resume_text):
    prompt = f"""
    You are a resume parsing assistant. Given the following resume text, extract the following details in a structured JSON format:

    - Name
    - Email
    - Phone_1
    - Address (Precise with city)
    - GitHub: Extract profile URL (look for patterns like github.com/username)"
    - LinkedIn: Extract profile URL (look for linkedin.com/in/ patterns)"
    - Professional_Experience_in_Years
    - Highest_Education
    - Skills
    - Applied_for_Profile (given in the resume or based on certifications, education, and skills)
    - Education (Include these EXACT field names):
        - University
        - Degree
        - Graduation_Date (use format 'Month YYYY' like 'May 2023')
    - Work_Experience (Include these fields):
        - Job_Title
        - Company
        - Start_Date (format: 'Month YYYY')
        - End_Date (format: 'Month YYYY' or 'Present')
        - Projects:
            - Project_Title
            - Description
    - Certifications

    - Achievements (List of notable achievements)

    - Suggested_Resume_Category (infer the most relevant job category based on skills, certifications, and work experience; do not use 'N/A')
    - Recommended_Additional_Skills (provide 3-5 concrete skills relevant to the Suggested_Resume_Category; do not use 'N/A')
    The resume text:
    {resume_text}

    Return the information in a clean and readable JSON format. Ensure all fields are included. For Suggested_Resume_Category and Recommended_Additional_Skills, infer values if not explicitly stated—avoid 'N/A'.
    """
    response = model.generate_content(prompt).text
    response_api = response.replace("```json", "").replace("```", "").strip()

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
            "Skills": [],
            "Applied_for_Profile": "N/A",
            "Education": [],
            "Work_Experience": [],
            "Certifications": [],
            "Suggested_Resume_Category": "N/A",
            "Achievements": [],
            "Recommended_Additional_Skills": []
        }

        # Set defaults for missing fields
        for field, default in required_top_level_fields.items():
            parsed_data.setdefault(field, default)

        # Ensure Certifications is a list
        parsed_data.setdefault("Certifications", [])
        if not isinstance(parsed_data["Certifications"], list):
            parsed_data["Certifications"] = [parsed_data["Certifications"]]
        parsed_data["Certifications"] = [
            c if c not in [None, "None", ""] else "N/A" 
            for c in parsed_data["Certifications"]
        ]
        if not parsed_data["Certifications"]:
            parsed_data["Certifications"] = ["N/A"]  

        # Ensure Graduation_Date exists in Education
        for edu in parsed_data.get("Education", []):
            edu.setdefault("Graduation_Date", "N/A")
            if edu["Graduation_Date"] in ["None", None, ""]:
                edu["Graduation_Date"] = "N/A"

        # Inside resume_details()
        for job in parsed_data.get("Work_Experience", []):
            job.setdefault("Start_Date", "N/A")
            job.setdefault("End_Date", "N/A")
            job.setdefault("Projects", [])  # Force initialize Projects field

            # Ensure each project has Title and Description
            for project in job.get("Projects", []):
                project.setdefault("Project_Title", "N/A")
                project.setdefault("Description", "N/A")

        # Ensure Recommended_Additional_Skills is a list
        if not isinstance(parsed_data.get("Recommended_Additional_Skills", []), list):
            parsed_data["Recommended_Additional_Skills"] = []

        # Convert 'None' to 'N/A'
        def convert_none(obj):
            if isinstance(obj, dict):
                return {k: convert_none(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_none(item) for item in obj]
            return obj if obj not in [None, "None"] else "N/A"
        
        parsed_data = convert_none(parsed_data)

        return parsed_data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    
def count_na(parsed_data):
    missing_fields = [] 
    _tracker(parsed_data, missing_fields)
    return len(missing_fields), missing_fields 

            

def display_in_container(title, value):
    if not value or (isinstance(value, list) and not value):
        value = "N/A"
    elif isinstance(value, list):
        value = f"<ul>{''.join([f'<li>{item}</li>' for item in value])}</ul>" if len(value) > 1 else value[0]
    else:
        value = str(value)  # Convert non-string values to string


    st.markdown(f"""
    <div style="margin-bottom: 2px;">
        <strong style="font-size: 14px; color: #1d3557; display: block;">{title}</strong>
        <div style="border: 2px solid #457b9d; border-radius: 10px; padding: 13px; background-color: #E5FBF6FF; 
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)
    

def display_parsed_data(parsed_data):
    if not parsed_data:
        st.error("Error: No valid resume data to display")
        return
    
    # Extract parsed data fields
    Full_Name = parsed_data.get("Name", "N/A")
    Email = parsed_data.get("Email", "N/A")
    Contacts = parsed_data.get('Phone_1', 'N/A')
    Address = parsed_data.get("Address", "N/A")
    LinkedIn = parsed_data.get("LinkedIn", "N/A")
    GitHub = parsed_data.get("GitHub", "N/A")
    Suggested_Resume_Category = parsed_data.get("Suggested_Resume_Category", "N/A")
    Applied_for_Profile = parsed_data.get("Applied_for_Profile", "N/A")
    Professional_Experience_in_Years = parsed_data.get("Professional_Experience_in_Years", "N/A")
    Highest_Education = parsed_data.get("Highest_Education", "N/A")
    Skills = parsed_data.get("Skills", [])
    Achievements = parsed_data.get("Achievements", ["N/A"])
    # References = parsed_data.get("References", [])
    Work_Experience = parsed_data.get("Work_Experience") or []

    # Initialize Professional_Experience_str as an empty list
    # Updated display logic in display_parsed_data() function
# Inside display_parsed_data()
    Work_Experience_str = []
    for job in Work_Experience:
        date_str = f"({job.get('Start_Date', 'N/A')} to {job.get('End_Date', 'N/A')})"
        job_entry = [
            f"{job.get('Job_Title', 'N/A')} at {job.get('Company', 'N/A')} {date_str}"
        ]
        
        # Always show projects section
        job_entry.append("<strong>Projects:</strong>")
        if job.get('Projects'):
            for project in job['Projects']:
                title = project.get('Project_Title', 'N/A')
                description = project.get('Description', 'N/A')
                job_entry.append(f"<strong>{title}</strong>: {description}")
        else:
            job_entry.append("N/A")
        
        Work_Experience_str.append("<br>".join(job_entry))
    # Ensure that Certifications is never empty and defaults to "N/A" if missing or empty
    Certifications = parsed_data.get("Certifications", ["N/A"])

    Education = parsed_data.get("Education", [])

    Education_str = []
    for edu in Education:
        degree = edu.get('Degree', 'N/A')
        university = edu.get('University', 'N/A')
        raw_date = edu.get('Graduation_Date', 'N/A')  # Note the corrected key name
        # Validate and format date
        if is_valid_date(raw_date):
            date_display = raw_date
        else:
            date_display = "N/A"
        Education_str.append(f"{degree} from {university} (Graduated: {date_display})")

    Suggested_Resume_Category = parsed_data.get("Suggested_Resume_Category", "N/A")
    
    Recommended_Additional_Skills = parsed_data.get("Recommended_Additional_Skills", [])
    


    # references_str = [
    #     f"{ref.get('Name', 'N/A')} ({ref.get('Designation', 'N/A')}) | "
    #     f"Email: {ref.get('Email', 'N/A')} | Phone: {ref.get('Phone', 'N/A')}"
    #     for ref in References
    # ] if References else ["N/A"]

    # Render data in containers using the function
    st.markdown(
        '''<div style='margin-top: 20px; text-align: center;'>
            <h3 style='color: #1d3557;'>Resume Analysis</h3>
        </div>''',
        unsafe_allow_html=True
    )
    st.markdown(f"<h6 style='font-size: 20px;'>Hi {Full_Name}! 😊</h6>", unsafe_allow_html=True)

    st.markdown(
        '''<div style='margin-top: 20px; text-align: center;'>
            <h5 style='color: #1d3557;'>Your Basic Information</h5>
        </div>''',
        unsafe_allow_html=True
    )
    st.write("Email:", Email)
    st.write("Contacts:", Contacts)
    st.write("Address:", Address)
    st.write("LinkedIn:", LinkedIn)
    st.write("GitHub:", GitHub)
    
    display_in_container("Suggested_Resume_Category", Suggested_Resume_Category)
    # Display each field with its respective value using the container function
    display_in_container("Profile Applied For", Applied_for_Profile)
    
    # Display Highest Education as a single value
    display_in_container("Highest Education", Highest_Education)
    
        # Display Education Details as a list
    display_in_container("Education ", Education_str)
    
        # Display Experience in Years as a single value
    display_in_container("Experience in Years", Professional_Experience_in_Years)
    # Display Skills as a list
    display_in_container("Skills", Skills) 

    # Display Professional Experience as a list
    display_in_container("Work Experience", Work_Experience_str)
    
    # Display Certifications as a list
    display_in_container("Certifications", Certifications)

    display_in_container("Achievements", Achievements)
    # display_in_container("References", references_str)

    # Display Recommended Additional Skills as a list
    display_in_container(f"Recommended Additional Skills for {Suggested_Resume_Category}", Recommended_Additional_Skills)
    st.caption("Adding these skills to resume will boost your chance of getting a job")