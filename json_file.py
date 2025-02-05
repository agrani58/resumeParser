import json
import random
import google.generativeai as genai
from dotenv import load_dotenv
import os
from collections import defaultdict
import re
from Courses import ds_course,web_course,android_course,uiux_course,ios_course
import streamlit as st
from ats import is_valid_date, _tracker
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

def display_in_container(title, value):
    if not value or (isinstance(value, list) and not value):
        value = "N/A"
    elif isinstance(value, list):
        # Simplify list rendering
        value = "<br>".join([str(item) for item in value])
    st.markdown(f"""
    <div style="margin-bottom: 2px;">
        <strong>{title}</strong>
            <div style="border: 2px solid #457b9d; border-radius: 10px; padding: 13px; 
                background-color: #E5FBF6FF; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);">
                {value}
            </div>
        </div>
        """, unsafe_allow_html=True)

        
def courses_recommendation(course_list):
    st.markdown(
        '''<div style='margin-top: 20px; text-align: center;'> <h5 style='color: #1d3557;'>Resume Tips & Tricks</h5></div>''',unsafe_allow_html=True
            )
    c=0
    rec_course=[]
    no_of_reco = st.slider('Choose Number of Courses You want to be Recommended',1,10,5)
    random.shuffle(course_list)
    for c_name,c_link in course_list:
        c+=1
        st.markdown(f'({c}) [{c_name}]({c_link})')
        rec_course.append(c_name)
        if c==no_of_reco:
            break
    return rec_course

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
    - Technical_Skills (list only technical/hard skills)
    - Soft_Skills (list only non-technical/soft skills)
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
        - Description
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
            "Technical_Skills": [],
            "Soft_Skills": [],
            "Applied_for_Profile": "N/A",
            "Certifications": [],
            "Suggested_Resume_Category": "N/A",
            "Achievements": [],
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
            if str(c).strip() not in ["", "N/A", "NONE", "none"]
        ]
        if not parsed_data["Certifications"]:
            parsed_data["Certifications"] = ["N/A"]

        # Convert remaining None values to N/A
        parsed_data = convert_none(parsed_data)
        return parsed_data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None



def display_parsed_data(parsed_data, missing_fields):
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
    Applied_for_Profile = parsed_data.get("Applied_for_Profile", "N/A")
    Professional_Experience_in_Years = parsed_data.get("Professional_Experience_in_Years", "N/A")
    Highest_Education = parsed_data.get("Highest_Education", "N/A")
    Technical_Skills = parsed_data.get("Technical_Skills", [])
    Soft_Skills = parsed_data.get("Soft_Skills", [])
    Achievements = parsed_data.get("Achievements", [])
    Work_Experience = parsed_data.get("Work_Experience", [])
    Work_Experience_str = []
    for job in Work_Experience:
        date_str = f"({job.get('Start_Date', 'N/A')} to {job.get('End_Date', 'N/A')})"
        raw_description = job.get("Description", "N/A")
        
        # Clean HTML tags from description
        if isinstance(raw_description, list):
            clean_description = " ".join([re.sub(r'<.*?>', '', str(item)) for item in raw_description])
        else:
            clean_description = re.sub(r'<.*?>', '', str(raw_description))
        
        # Convert description into bullet points using '-' for new points.
        # Split on period followed by whitespace (this assumes each sentence ends with a period).
        sentences = re.split(r'\.\s+', clean_description.strip())
        # Remove any empty sentences and re-add a period if needed.
        bulleted_description = '<br>'.join(f"-- {sentence.strip()}" for sentence in sentences if sentence.strip())
        
        job_entry = f"""<strong>• {job.get('Job_Title', 'N/A')}</strong> at {job.get('Company', 'N/A')} {date_str}<br>
    <strong>Description:</strong> {bulleted_description}"""
        
        Work_Experience_str.append(job_entry)

    # Process Projects
    Projects = parsed_data.get("Projects", [])
    Projects_str = []
    for project in Projects:
        raw_description = project.get("Description", "N/A")
        
        # Clean HTML tags from description
        if isinstance(raw_description, list):
            clean_description = " ".join([re.sub(r'<.*?>', '', str(item)) for item in raw_description])
        else:
            clean_description = re.sub(r'<.*?>', '', str(raw_description))
        
        # Convert description into bullet points using '-' for new points.
        sentences = re.split(r'\.\s+', clean_description.strip())
        bulleted_description = '<br>'.join(f"- {sentence.strip()}" for sentence in sentences if sentence.strip())
        
        project_entry = f"""<p><strong>• {project.get('Project_Title', 'N/A')}</strong></p>
    <p><strong>Description:</strong> {bulleted_description}</p>"""
        
        Projects_str.append(project_entry)
    # Certifications Processing
    Certifications = parsed_data.get("Certifications", ["N/A"])

    # Education Processing
    Education = parsed_data.get("Education", [])
    Education_str = []
    for edu in Education:
        raw_date = edu.get('Graduation_Date', 'N/A')
        date_display = raw_date if is_valid_date(raw_date) else "N/A"
        
        Education_str.append(
            f"{edu.get('Degree', 'N/A')} from {edu.get('University', 'N/A')} (Graduated: {date_display})"
        )

    Suggested_Resume_Category = parsed_data.get("Suggested_Resume_Category", "N/A")
    Recommended_Additional_Skills = parsed_data.get("Recommended_Additional_Skills", [])

    # UI Rendering
    st.markdown(
        f"<div style='margin-top: -20px; margin-left:-110px'><h4>Hello {Full_Name}! 😊</h4></div>", 
        unsafe_allow_html=True
    )

    st.markdown("""
        <style>
            .warning-text {
                font-size: 12px;
                color: red;
                margin-top: -6px !important; /* Reduce spacing */
            }
        </style>
        """, unsafe_allow_html=True)

    st.markdown(
        '''<div style=' text-align: center;'>
            <h4 style='color: #1d3557;'>Resume Analysis</h4>
        </div>''',
        unsafe_allow_html=True
    )

    st.markdown(
        '''<div style='margin-top: 10px; text-align:center'>
            <h5 style='color: #1d3557;'>Your Basic Information</h5>
        </div>''',
        unsafe_allow_html=True
    )
    
    # Personal Info Columns with Warning Styling
    # col1, col2 = st.columns(2)
    # with col1:
    st.write("Email:", Email)
    if "Email" in structured_missing and structured_missing["Email"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Email</div>', unsafe_allow_html=True)

    st.write("Contacts:", Contacts)
    if "Phone_1" in structured_missing and structured_missing["Phone_1"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Contacts</div>', unsafe_allow_html=True)

    st.write("Address:", Address)
    if "Address" in structured_missing and structured_missing["Address"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Address</div>', unsafe_allow_html=True)
    
    # with col2:
    st.write("LinkedIn:", LinkedIn)
    if "LinkedIn" in structured_missing and structured_missing["LinkedIn"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Include LinkedIn Profile URL</div>', unsafe_allow_html=True)
                
    st.write("GitHub:", GitHub)
    if "GitHub" in structured_missing and structured_missing["GitHub"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Include GitHub Profile URL</div>', unsafe_allow_html=True)
    
    st.write("Profile Applied For:", Applied_for_Profile)
    if "Applied_for_Profile" in structured_missing and structured_missing["Applied_for_Profile"].get("_top", 0) > 0:
        st.markdown(
            '<div class="warning-text">⚠️ Your resume does not specify Target Job Profile</div>',
            unsafe_allow_html=True
        )
    # Main Content Sections
    display_in_container("Suggested Resume Category:", Suggested_Resume_Category)
    if "Suggested_Resume_Category" in structured_missing and structured_missing["Suggested_Resume_Category"].get("_top", 0) > 0:
        st.markdown(
            '<div class="warning-text">⚠️ Suggested Resume Category will be displayed when your resume is ATS compatible</div>',
            unsafe_allow_html=True
        )
    # Education Section
    with st.expander("🎓 Your Education", expanded=True):
        display_in_container("Highest Education", Highest_Education)
        if "Highest_Education" in structured_missing and structured_missing["Highest_Education"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Include Education Field clearly</div>',
                unsafe_allow_html=True
            )

        display_in_container("Education Details", Education_str)

        # Education Validation Warnings
        grad_missing = structured_missing.get("Education", {}).get("Graduation_Date", 0)
        degree_missing = structured_missing.get("Education", {}).get("Degree", 0)
        university_missing = structured_missing.get("Education", {}).get("University", 0)

        if grad_missing > 0:
            st.markdown(f'<div class="warning-text">⚠️ Missing Graduation Date ({grad_missing} entries)</div>', unsafe_allow_html=True)
        if degree_missing > 0:
            st.markdown(f'<div class="warning-text">⚠️ Missing Degree ({degree_missing} entries)</div>', unsafe_allow_html=True)
        if university_missing > 0:
            st.markdown(f'<div class="warning-text">⚠️ Missing University ({university_missing} entries)</div>', unsafe_allow_html=True)

    # Work Experience Section
    with st.expander("💼 Your Work History", expanded=True):
        display_in_container("Professional Experience", f"{Professional_Experience_in_Years} years")
        if "Professional_Experience_in_Years" in structured_missing and structured_missing["Professional_Experience_in_Years"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Add Years of Experience in Work Experience</div>',
                unsafe_allow_html=True
            )

        display_in_container("Work Experience Details", Work_Experience_str)

        # Date Validation
        dates_missing = (
            structured_missing.get("Work_Experience", {}).get("Start_Date", 0) +
            structured_missing.get("Work_Experience", {}).get("End_Date", 0)
        )
        if dates_missing > 0:
            st.markdown(
                f'<div class="warning-text">⚠️ Missing Dates in {dates_missing} job entries</div>',
                unsafe_allow_html=True
            )
            
        description_missing= structured_missing.get("Work_Experience",{}).get("Description",0)
        if description_missing>0:
            st.markdown(f'<div class="warning-text"⚠️ Missing Descriptions in {description_missing} job entries</div>',
            unsafe_allow_html=True) 

    # Projects Section
    with st.expander("🛠️ Your Projects", expanded=True):
        display_in_container("Project Details", Projects_str)
        projects_missing = structured_missing.get("Projects", {})
        title_missing = projects_missing.get("Project_Title", 0)
        desc_missing = projects_missing.get("Description", 0)

        if title_missing > 0:
            st.markdown(
                f'<div class="warning-text">⚠️ Missing Project Titles in {title_missing} entries</div>',
                unsafe_allow_html=True
            )
        if desc_missing > 0:
            st.markdown(
                f'<div class="warning-text">⚠️ Missing Descriptions in {desc_missing} projects</div>',
                unsafe_allow_html=True
            )
        if len(Projects) == 0:
            st.markdown(
                '<div class="warning-text">⚠️ No projects found in resume</div>',
                unsafe_allow_html=True
            )

    # Skills Section
    with st.expander("🔧 Your Skills", expanded=True):
        display_in_container("Technical Skills", Technical_Skills)
        if "Technical_Skills" in structured_missing and structured_missing["Technical_Skills"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Include More Technical Skills</div>',
                unsafe_allow_html=True
            )

        display_in_container("Soft Skills", Soft_Skills)
        if "Soft_Skills" in structured_missing and structured_missing["Soft_Skills"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Include More Soft Skills</div>',
                unsafe_allow_html=True
            )

    # Certifications & Achievements Section
    with st.expander("🏆 Your Certifications & Achievements", expanded=True):
        display_in_container("Certifications", Certifications)
        if "Certifications" in structured_missing and structured_missing["Certifications"].get("_top", 0) > 0:
            st.markdown(
                f'<div class="warning-text">⚠️ Missing {structured_missing["Certifications"]["_top"]} Certifications</div>',
                unsafe_allow_html=True
            )

        display_in_container("Achievements", Achievements)
        if "Achievements" in structured_missing and structured_missing["Achievements"].get("_top", 0) > 0:
            st.markdown(
                '<div class="warning-text">⚠️ Include More Achievements</div>',
                unsafe_allow_html=True
            )

    # Recommendations Section
    display_in_container(f"🌟 Recommended Skills for {Suggested_Resume_Category}", Recommended_Additional_Skills)
    st.caption("Adding these skills to resume will boost your chance of getting a job")