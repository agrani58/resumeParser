import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import streamlit as st

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
    - Linkedin
    - GitHub (Extract profile URL if found in text, even if not labeled)
    - Professional_Experience_in_Years
    - Highest_Education
    - Skills
    - Applied_for_Profile (given in the resume or based on certifications,education and skills )
    - Education (Include these EXACT field names):
        - University
        - Degree 
        - Graduation_Date (use format 'Month YYYY' like 'May 2023')
    - Professional_Experience (is also known as work experience.Include Job Title, Company, Years of Experience)
    - Certifications
    - Suggested_Resume_Category (infer the most relevant job category based on skills, certifications, and work experience; do not use 'N/A')
    - Recommended_Additional_Skills (provide 3-5 concrete skills relevant to the Suggested_Resume_Category; do not use 'N/A')
    The resume text:
    {resume_text}

    Return the information in a clean and readable JSON format. Ensure all fields are included. For Suggested_Resume_Category and Recommended_Additional_Skills, infer values if not explicitly stated—avoid 'N/A'.
    """
    response = model.generate_content(prompt).text
    response_api = response.replace("```json", "").replace("```", "").strip()
    
    # # ADD THIS LINE TO CONVERT "None" TO "N/A"
    # response_api = response_api.replace('"None"', '"N/A"').replace("'None'", "'N/A'")
    try:
        parsed_data = json.loads(response_api)
        # Ensure all fields are present and properly formatted
        parsed_data.setdefault("Name", "N/A")
        parsed_data.setdefault("Phone_1","N/A")
        parsed_data.setdefault("Github", "N/A")
        parsed_data.setdefault("Email", "N/A")
        parsed_data.setdefault("Address","N/A")
        parsed_data.setdefault("Github", "N/A")
        parsed_data.setdefault("Linkedin", "N/A")
        parsed_data.setdefault("Address","N/A")
        parsed_data.setdefault("Github", "N/A")
        parsed_data.setdefault("Highest_Education", "N/A")
        
                # Handle Education and Experience defaults
        for edu in parsed_data.get("Education", []):
    # Handle different key variants
            edu["Graduation Date"] = edu.get("Graduation_Date", "N/A")  # Catch alternate spellings
        
        if parsed_data["Highest_Education"] not in [edu["Degree"] for edu in parsed_data.get("Education", [])]:
            parsed_data["Highest_Education"] = "N/A"
        # Infer Suggested_Resume_Category if N/A
        if parsed_data["Suggested_Resume_Category"] == "N/A":
            Applied_for_Profile = parsed_data.get("Applied_for_Profile", [])
            if isinstance(Applied_for_Profile, list) and len(Applied_for_Profile) > 0:
                parsed_data["Suggested_Resume_Category"] = Applied_for_Profile[0]
        
        # Ensure Recommended_Additional_Skills is a list and not N/A
        ras = parsed_data.get("Recommended_Additional_Skills", [])
        if not isinstance(ras, list):
            parsed_data["Recommended_Additional_Skills"] = []

        for job in parsed_data.get("Professional_Experience", []):
            job.setdefault("Company", "N/A")
            job.setdefault("Job Title", "N/A")
            job.setdefault("Years of Experience", "N/A")
        return parsed_data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None

def count_na(parsed_data):

    missing = []
    
    def _tracker(data, path=""):
        if isinstance(data, dict):
            for k, v in data.items(): #k is path, v is value 
                new_path = f"{path}.{k}" if path else k #ternery operation
                if v in ["N/A", "None", None]:  
                    missing.append(new_path) #adds path to missing list 
                else:
                    _tracker(v, new_path) 
        elif isinstance(data, list):
            for i, item in enumerate(data):
                _tracker(item, f"{path}[{i}]")
    
    _tracker(parsed_data)
    return len(missing), missing

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
    Linkedin = parsed_data.get("Linkedin", "N/A")
    Github = parsed_data.get("Github", "N/A")
    Suggested_Resume_Category=parsed_data.get("Suggested_Resume_Category","N/A")
    Applied_for_Profile = parsed_data.get("Applied_for_Profile", "N/A")
    Professional_Experience_in_Years = parsed_data.get("Professional_Experience_in_Years", "N/A")
    Highest_Education = parsed_data.get("Highest_Education", "N/A")
    Skills = parsed_data.get("Skills", [])
    
    Professional_Experience = parsed_data.get("Professional_Experience") or parsed_data.get("Work_Experience") or []
    
    if Professional_Experience:
        Professional_Experience_str = [
            f"{job.get('Job Title', 'N/A')} at {job.get('Company', 'N/A')} "
            f"({job.get('Years of Experience')})"  # Add date calculation function
            for job in Professional_Experience 
            if any(val != "N/A" for val in job.values())
        ]
    else:
        Professional_Experience_str = ["No Professional Experience Data Available"]

    Education = parsed_data.get("Education", [])
    if Education:
        Education_str = [f"{edu.get('Degree', 'N/A')} from {edu.get('University', 'N/A')} (Graduated: {edu.get('Graduation Date', 'N/A')})"
                        for edu in Education]
    else:
        Education_str = ["N/A"]
        
    Certifications = parsed_data.get("Certifications", [])
    na_count = count_na(parsed_data)
    Suggested_Resume_Category = parsed_data.get("Suggested_Resume_Category", "N/A")
    
    Recommended_Additional_Skills = parsed_data.get("Recommended_Additional_Skills", [])


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
    st.write("Linkedin:", Linkedin)
    st.write("Github:", Github)
    
    display_in_container("Suggested_Resume_Category",Suggested_Resume_Category)
    # Display each field with its respective value using the container function
    display_in_container("Profile Applied For", Applied_for_Profile)
    
    # Display Skills as a list
    display_in_container("Skills", Skills) 

    # Display Highest Education as a single value
    display_in_container("Highest Education", Highest_Education)

    # Display Education Details as a list
    display_in_container("Education Details", Education_str)

    # Display Experience in Years as a single value
    display_in_container("Experience in Years", Professional_Experience_in_Years)

    # Display Professional Experience as a list
    display_in_container("Professional Experience", Professional_Experience_str)

    # Display Certifications as a list
    display_in_container("Certifications", Certifications)

    # Display Recommended Additional Skills as a list
    display_in_container(f"Recommended Additional Skills for {Suggested_Resume_Category}", Recommended_Additional_Skills)
    st.caption("Adding these skills to resume will boost your chance of getting a job")
    
