import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
from collections import defaultdict
import re
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
    - Suggested_Resume_Category (infer the most relevant job category based on skills, certifications, and work experience)
    - Recommended_Additional_Skills (provide 3-5 concrete skills relevant to the Suggested_Resume_Category)
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
        # In resume_details function:
        parsed_data.setdefault("Certifications", [])
        # Ensure it's always a list
        if isinstance(parsed_data["Certifications"], str):
            parsed_data["Certifications"] = [parsed_data["Certifications"]]
        # Filter invalid entries
        parsed_data["Certifications"] = [
            str(c).strip() for c in parsed_data["Certifications"] 
            if str(c).strip().lower() not in ["", "n/a", "none"]
        ]
        # Set to ["N/A"] only if truly empty
        if not parsed_data["Certifications"]:
            parsed_data["Certifications"] = ["N/A"]
            
        for edu in parsed_data.get("Education", []):
            edu.setdefault("Graduation_Date", "N/A")
            current_date = edu["Graduation_Date"]
            if not is_valid_date(current_date):
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
    

def display_parsed_data(parsed_data,missing_fields):
    if not parsed_data:
        st.error("Error: No valid resume data to display")
        return
        # Process missing fields into structured format
    structured_missing = defaultdict(lambda: defaultdict(int))
    for path in missing_fields:
        clean_path = re.sub(r'\[\d+\]', '', path)  # Remove array indices
        parts = clean_path.split('.', 1)
        top_field = parts[0]
        if len(parts) > 1:
            sub_field = parts[1]
            structured_missing[top_field][sub_field] += 1
        else:
            structured_missing[top_field]["_top"] += 1
            
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
            # After Work Experience section
    
    # Ensure that Certifications is never empty and defaults to "N/A" if missing or empty
    Certifications = parsed_data.get("Certifications", ["N/A"])

    Education = parsed_data.get("Education", [])

    # In display_parsed_data() - Education section
    Education_str = []
    for edu in Education:
        raw_date = edu.get('Graduation_Date', 'N/A')
        date_display = raw_date if is_valid_date(raw_date) else "N/A"
        Education_str.append(
            f"{edu.get('Degree', 'N/A')} from {edu.get('University', 'N/A')} "
            f"(Graduated: {date_display})"
        )

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
    
    
    st.markdown("""
        <style>
            .warning-text {
                font-size: 12px;
                color: red;
                margin-top: 5px !important; /* Reduce spacing */
            }
        </style>
        """, unsafe_allow_html=True)


    st.write("Email:", Email)
    if "Email" in structured_missing:
        if structured_missing["Email"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Email</div>', unsafe_allow_html=True)

    st.write("Contacts:", Contacts)
    if "Contacts" in structured_missing:
        if structured_missing["Contacts"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Contacts</div>', unsafe_allow_html=True)

    st.write("Address:", Address)
    if "Address" in structured_missing:
        if structured_missing["Address"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Address</div>', unsafe_allow_html=True)

    st.write("LinkedIn:", LinkedIn)  # Check for missing LinkedIn
    if "LinkedIn" in structured_missing:
        if structured_missing["LinkedIn"].get("_top", 0) > 0:
            st.markdown('<div style="color: red; margin-top: -20px;font-size: 12px;">⚠️ Include LinkedIn Profile URL</div>', unsafe_allow_html=True)
            
    st.write("GitHub:", GitHub)
    if "GitHub" in structured_missing:
        if structured_missing["GitHub"].get("_top", 0) > 0:
            st.markdown('<div style="color: red; margin-top: -20px;font-size: 12px;">⚠️ Include GitHub Profile URL</div>', unsafe_allow_html=True)

    display_in_container("Suggested_Resume_Category", Suggested_Resume_Category)
    if "Suggested_Resume_Category" in structured_missing:
        if structured_missing["Suggested_Resume_Category"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Suggested Resume Category will be displayed when your resume is ATS compatible</div>',
                unsafe_allow_html=True
            )
            
    # Profile Applied For
    display_in_container("Profile Applied For", Applied_for_Profile)
    if "Applied_for_Profile" in structured_missing:
        if structured_missing["Applied_for_Profile"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Your resume does not specify Target Job Profile</div>',
                unsafe_allow_html=True
            )
    
    # Display Highest Education as a single value

    display_in_container("Highest Education", Highest_Education)
    if "Highest_Education" in structured_missing:
        if structured_missing["Highest_Education"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Include Education Field clearly </div>',
                unsafe_allow_html=True
            )
    
    # Display Education Details as a list
    display_in_container("Education ", Education_str)
    # After Education section
# Initialize variables with default values
    grad_missing = 0
    degree_missing = 0
    university_missing = 0

# In display_parsed_data() - Education validation section
    if "Education" in structured_missing:
        grad_missing = structured_missing["Education"].get("Graduation_Date", 0)  # Exact field name
        degree_missing = structured_missing["Education"].get("Degree", 0)
        university_missing = structured_missing["Education"].get("University", 0)
    # Now check each variable
    if grad_missing > 0:
        msg = "⚠️ Include Graduation Date"
        if grad_missing > 1:
            msg += f" ({grad_missing} entries)"
        st.markdown(f'<div class="warning-text">{msg}</div>', unsafe_allow_html=True)

    if degree_missing > 0:
        msg = "⚠️ Include Degree"
        if degree_missing > 1:
            msg += f" ({degree_missing} entries)"
        st.markdown(f'<div class="warning-text">{msg}</div>', unsafe_allow_html=True)

    if university_missing > 0:
        msg = "⚠️ Include University"
        if university_missing > 1:
            msg += f" ({university_missing} entries)"
        st.markdown(f'<div class="warning-text">{msg}</div>', unsafe_allow_html=True)
        # Display Experience in Years as a single value
    display_in_container("Experience in Years", Professional_Experience_in_Years)
    if "Professional_Experience_in_Years" in structured_missing:
        if structured_missing["Professional_Experience_in_Years"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Add Years of Experience in Work Experience</div>',
                unsafe_allow_html=True
            )

    # Display Skills as a list
    display_in_container("Skills", Skills)
    if "Skills" in structured_missing:
        total_skills_issues = sum(structured_missing["Skills"].values())
        if total_skills_issues > 0:
            msg = "⚠️ Improve Skills Section"
            if total_skills_issues > 1:
                msg += f" ({total_skills_issues} issues found)"
            st.markdown(
                f'<div class="warning-text">{msg}</div>',
                unsafe_allow_html=True
            )
    # Inside display_parsed_data() function, after processing Work_Experience_str
# Add this line to actually display the work experience container
    display_in_container("Work Experience", Work_Experience_str)
    if "Work_Experience" in structured_missing:
        projects_missing = structured_missing["Work_Experience"].get("Projects", 0)
        dates_missing = (
            structured_missing["Work_Experience"].get("Start_Date", 0) +
            structured_missing["Work_Experience"].get("End_Date", 0)
        )
        if projects_missing > 0:
            msg = "⚠️ Include Project Details"
            if projects_missing > 1:
                msg += f" ({projects_missing} entries)"
            st.markdown(f'<div class="warning-text">{msg}</div>',
                        unsafe_allow_html=True)
        if dates_missing > 0:
            msg = "⚠️ Include Job Dates"
            st.markdown(f'<div class="warning-text">{msg}</div>',
                        unsafe_allow_html=True)
    # Display Certifications as a list
    # After Certifications section
    display_in_container("Certifications", Certifications)
    if "Certifications" in structured_missing:
        cert_missing = structured_missing["Certifications"].get("_top", 0)
        if cert_missing > 0:
            msg = "⚠️ Include Certifications"
            if cert_missing > 1:
                msg += f" ({cert_missing} entries)"
            st.markdown(f'<div class="warning-text">{msg}</div>', 
                        unsafe_allow_html=True)
    display_in_container("Achievements", Achievements)
    if "Achievements" in structured_missing:
        achieve_missing = structured_missing["Achievements"].get("_top", 0)
        if achieve_missing > 0:
            st.markdown('<div class="warning-text">⚠️ Include Achievements</div>',
                        unsafe_allow_html=True)
    # Display Recommended Additional Skills as a list
    display_in_container(f"Recommended Additional Skills for {Suggested_Resume_Category}", Recommended_Additional_Skills)
    st.caption("Adding these skills to resume will boost your chance of getting a job")
