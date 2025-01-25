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

def determine_experience_level(experience_years, job_titles):
    # Define possible job titles and their corresponding experience levels
    entry_level_titles = ['Junior', 'Intern', 'Assistant', 'Entry-level']
    mid_level_titles = ['Mid', 'Manager', 'Lead', 'Specialist']
    senior_level_titles = ['Senior', 'Director', 'Principal', 'Head']
    executive_level_titles = ['Executive', 'VP', 'C-suite', 'Chief']

    # Check job titles first
    for title in job_titles:
        title_lower = title.lower()
        if any(level in title_lower for level in entry_level_titles):
            return "Entry-level"
        elif any(level in title_lower for level in mid_level_titles):
            return "Mid-level"
        elif any(level in title_lower for level in senior_level_titles):
            return "Senior-level"
        elif any(level in title_lower for level in executive_level_titles):
            return "Executive"
    return "N/A"  # Default if no level is determined

def parse_experience_years(experience_str):
    """Parse the experience years, handling cases like '5+' and '6 Months'."""
    try:
        if '+' in experience_str:
            return experience_str  # Keep the original '5+' format
        if 'Month' in experience_str:
            months = int(experience_str.split(' ')[0])
            return f"{months} months"
        return f"{int(experience_str)} years"
    except ValueError:
        return "N/A"  # Return N/A if the experience value is invalid or missing

def resume_details(resume):
    prompt = f"""
    You are a resume parsing assistant. Given the following resume text, extract the following details in a structured JSON format:

    - Name
    - Email
    - Phone_1
    - Phone_2
    - Address (Precise with city)
    - Linkedin
    - Github
    - Professional_Experience_in_Years
    - Highest_Education
    - Skills
    - Applied_for_Profile (given in the resume or based on certifications,education and skills )
    - Education (Include University Name, Degree, GPA)
    - Professional_Experience (Include Job Title, Company, Years of Experience)
    - Certifications
    - Suggested Resume Category (based on certifications and  skills)
    - Recommended Additional Skills (based on current skills, professional experience and certifications)

    The resume text:
    {resume}

    Return the information in a clean and readable JSON format. Ensure that all fields are included, even if their value is "N/A".
    """
    response = model.generate_content(prompt).text
    response_clean = response.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(response_clean)
        # Ensure all fields are present
        data.setdefault("Address", "N/A")
        data.setdefault("City", "N/A")
        data.setdefault("Suggested_Resume_Category", "N/A")  # Ensure this is always included
        data.setdefault("Recommended_Additional_Skills", ["N/A"])  # Ensure this is always a list

        # Determine experience level based on job titles and years of experience
        job_titles = [job.get("Job Title", "") for job in data.get("Professional_Experience", [])]
        experience_years = data.get("Professional_Experience_in_Years", "0")


        return data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None

def display_in_container(title, value):
    if value is None or (isinstance(value, list) and len(value) == 0):
        value = "N/A"  # Handle empty or None values
    elif isinstance(value, list):
        if len(value) > 1:
            value = "<ul>" + "".join([f"<li>{item}</li>" for item in value]) + "</ul>"
        else:
            value = value[0] if len(value) == 1 else "N/A"  # Handle single-item lists
    elif not isinstance(value, str):
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

def display_parsed_data(data):
    if not data:
        st.error("Error: No valid resume data to display")
        return

    # Extract parsed data fields
    Full_Name = data.get("Name", "N/A")
    Email = data.get("Email", "N/A")
    Contacts = f"Phone 1: {data.get('Phone_1', 'N/A')}\nPhone 2: {data.get('Phone_2', 'N/A')}"
    Address = data.get("Address", "N/A")
    Linkedin = data.get("Linkedin", "N/A")
    Github = data.get("Github", "N/A")
    Applied_for_Profile = data.get("Applied_for_Profile", "N/A")
    Professional_Experience_in_Years = data.get("Professional_Experience_in_Years", "N/A")
    Highest_Education = data.get("Highest_Education", "N/A")
    Skills = data.get("Skills", [])
    
    Education = data.get("Education", [])
    if Education:
        Education_str = [f"{edu.get('Degree', 'N/A')} from {edu.get('University', 'N/A')} (Graduated: {edu.get('Graduation Date', 'N/A')})"
                        for edu in Education]
    else:
        Education_str = ["N/A"]

    Professional_Experience = data.get("Professional_Experience", [])
    if Professional_Experience:
        Professional_Experience_str = [f"{job.get('Job Title', 'N/A')} at {job.get('Company', 'N/A')} ({job.get('Years of Experience', 'N/A')})"
                                    for job in Professional_Experience]
    else:
        Professional_Experience_str = ["No Professional Experience Data Available"]
    
    Certifications = data.get("Certifications", [])
    Suggested_Resume_Category = data.get("Suggested_Resume_Category", "N/A")
    Recommended_Additional_Skills = data.get("Recommended_Additional_Skills", ["N/A"])  # Ensure this is always a list
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
    st.caption("Adding these skills to resume will boost yoru chance of getting a job")
