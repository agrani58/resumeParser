from collections import defaultdict

import re
import time
import streamlit as st

from app.utils import fetch_yt_video, is_valid_date,courses_recommendation, resume_score
        
from app.liks import ds_course, web_course, android_course, ios_course, uiux_course,software_dev_course,qa_course

    # Full width container for tips

def display_in_container(title, value):
    if not value or (isinstance(value, list) and not value):
        value = "N/A"
    elif isinstance(value, list):
        value = "<br>".join([str(item) for item in value])
    st.markdown(f"""
        <div style="margin-bottom: 2px;">
            <strong>{title}</strong>
            <div style="border: 2px solid #CEE8FAFF; border-radius: 10px; margin-bottom: 0.8rem; padding: 13px; 
                        background: linear-gradient(to right, #CEE8FAFF, #F1E4FAFF);
                        ">
                {value}
            </div>
        </div>
    """, unsafe_allow_html=True)


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
    processed_data = {
        "Full_Name": parsed_data.get("Name", "N/A"),
        "Email": parsed_data.get("Email", "N/A"),
        "Contacts": parsed_data.get('Phone_1', 'N/A'),
        "Address": parsed_data.get("Address", "N/A"),
        "LinkedIn": parsed_data.get("LinkedIn", "N/A"),
        "GitHub" :parsed_data.get("GitHub", "N/A"),
        "Applied_for_Profile": parsed_data.get("Applied_for_Profile", "N/A"),
        "Professional_Experience_in_Years" :parsed_data.get("Professional_Experience_in_Years", "N/A"),
        "Highest_Education": parsed_data.get("Highest_Education", "N/A"),
        "Technical_Skills" : parsed_data.get("Technical_Skills", []),
        "Soft_Skills" : parsed_data.get("Soft_Skills", []),
        "Achievements": parsed_data.get("Achievements", []),
        "Work_Experience":parsed_data.get("Work_Experience", []),
        "Certifications": parsed_data.get("Certifications", ["N/A"]),
        "Education": parsed_data.get("Education", []),
        "Projects": parsed_data.get("Projects", []),
        "missing_fields":missing_fields,
        "Suggested_Resume_Category": parsed_data.get("Suggested_Resume_Category", "N/A"),
        "Recommended_Additional_Skills": parsed_data.get("Recommended_Additional_Skills", []),  
        "Hobbies": parsed_data.get("Hobbies", [])  
            
    }
    display_parsed_data_ui(processed_data, structured_missing)



def display_parsed_data_ui(processed_data, structured_missing):
    # Unpack processed_data
    Full_Name = processed_data["Full_Name"]
    Email = processed_data["Email"]
    Contacts = processed_data["Contacts"]
    Address = processed_data["Address"]
    LinkedIn = processed_data["LinkedIn"]
    GitHub = processed_data["GitHub"]
    Applied_for_Profile = processed_data["Applied_for_Profile"]
    Professional_Experience_in_Years = processed_data["Professional_Experience_in_Years"]
    Highest_Education = processed_data["Highest_Education"]
    Technical_Skills = processed_data["Technical_Skills"]
    Soft_Skills = processed_data["Soft_Skills"]
    Achievements = processed_data["Achievements"]
    Work_Experience = processed_data["Work_Experience"]
    Certifications = processed_data["Certifications"]
    Education = processed_data["Education"]
    Projects = processed_data["Projects"]
    Suggested_Resume_Category = processed_data["Suggested_Resume_Category"]
    Recommended_Additional_Skills = processed_data["Recommended_Additional_Skills"]
    Hobbies= processed_data["Hobbies"] 
    missing_fields = processed_data.get('missing_fields', [])
    # Process Work Experience
    Work_Experience_str = []
    for job in Work_Experience:
        date_str = f"({job.get('Start_Date', 'N/A')} to {job.get('End_Date', 'N/A')})"
        raw_description = job.get("Description", "N/A")
        
        if isinstance(raw_description, list):
            clean_description = " ".join([re.sub(r'<.*?>', '', str(item)) for item in raw_description])
        else:
            clean_description = re.sub(r'<.*?>', '', str(raw_description))
        
        sentences = re.split(r'\.\s+', clean_description.strip())
        bulleted_description = '<br>'.join(f"-- {sentence.strip()}" for sentence in sentences if sentence.strip())
        
        job_entry = f"""<strong>• {job.get('Job_Title', 'N/A')}</strong> at {job.get('Company', 'N/A')} {date_str}<br>
        <strong>Description:</strong> {bulleted_description}"""
        Work_Experience_str.append(job_entry)

    # Process Projects
    Projects_str = []
    for project in Projects:
        raw_description = project.get("Description", "N/A")
        
        if isinstance(raw_description, list):
            clean_description = " ".join([re.sub(r'<.*?>', '', str(item)) for item in raw_description])
        else:
            clean_description = re.sub(r'<.*?>', '', str(raw_description))
        
        sentences = re.split(r'\.\s+', clean_description.strip())
        bulleted_description = '<br>'.join(f"- {sentence.strip()}" for sentence in sentences if sentence.strip())
        
        project_entry = f"""<p><strong>• {project.get('Project_Title', 'N/A')}</strong></p>
        <p><strong>Description:</strong> {bulleted_description}</p>"""
        Projects_str.append(project_entry)

    # Process Education
    Education_str = []
    for edu in Education:
        raw_date = edu.get('Graduation_Date', 'N/A')
        date_display = raw_date if is_valid_date(raw_date) else "N/A"
        Education_str.append(
            f"{edu.get('Degree', 'N/A')} from {edu.get('University', 'N/A')} (Graduated: {date_display})")

    

    st.markdown(
        f"""<div style='margin-left:-7rem; margin-top: -1.5rem;'><h4 style='color: #1d3557;'> Hello {Full_Name}! 😊</h4></div>""",unsafe_allow_html=True  )

    st.markdown("""
        <style>
            .warning-text {
                font-size: 12px;
                color: red;
                margin-top: -6px !important;
                margin-bottom: 10px !important;
            }
        </style>
        """, unsafe_allow_html=True)

    st.markdown(
        '''<div style=' text-align: center; margin-top:1rem';><h4 style='color: #1d3557;'>Resume Analysis</h4></div>''',unsafe_allow_html=True)

    st.markdown(
        '''<div style='margin-top: 1rem;margin-bottom: 0.7rem; text-align:center'><h5 style='color: #1d3557;'>Your Basic Information</h5></div>''',unsafe_allow_html=True)

    # Personal Info Columns with Warning Styling
    col1,col2,col3=st.columns([1,0.1,1])
    with col1:
        st.write("Email:", Email)
        if "Email" in structured_missing and structured_missing["Email"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Email</div>', unsafe_allow_html=True)

        st.write("Contacts:", Contacts)
        if "Phone_1" in structured_missing and structured_missing["Phone_1"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Contacts</div>', unsafe_allow_html=True)

        st.write("Address:", Address)
        if "Address" in structured_missing and structured_missing["Address"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Must Include Address</div>', unsafe_allow_html=True)
    with col3:
        st.write("LinkedIn:", LinkedIn)
        if "LinkedIn" in structured_missing and structured_missing["LinkedIn"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Include LinkedIn Profile URL</div>', unsafe_allow_html=True)

        st.write("GitHub:", GitHub)
        if "GitHub" in structured_missing and structured_missing["GitHub"].get("_top", 0) > 0:
            st.markdown('<div class="warning-text">⚠️ Include GitHub Profile URL</div>', unsafe_allow_html=True)

    display_in_container("Profile Applied For:", Applied_for_Profile)
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
    with st.expander("🎓 Your Education", expanded=False):
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
    with st.expander("💼 Your Work History", expanded=False):
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
        if len(Work_Experience) == 0:
            st.markdown(
            '''<div class="warning-text">⚠️ No work experience found in resume</div>''',
            unsafe_allow_html=True
        )

    # Projects Section
    with st.expander("🛠️ Your Projects", expanded=False):
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
    with st.expander("🔧 Your Skills", expanded=False):
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
    with st.expander("🏆 Your Certifications & Achievements", expanded=False):
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
            
    with st.expander("Hobbies & Interests", expanded=False):
        display_in_container("Hobbies & Interests", Hobbies)
        if "Hobbies" in structured_missing and structured_missing["Hobbies"].get("_top", 0) > 0:
                st.markdown(
                    '<div class="warning-text">⚠️ Including hobbies shows well-rounded personality</div>',
                    unsafe_allow_html=True
                )
        st.caption("*Not a Mandatory Category*")


def profiles_match(applied, suggested):
    # Normalize both job titles to lowercase and strip leading/trailing spaces
    applied_clean = applied.lower().strip()
    suggested_clean = suggested.lower().strip()
    
    # Split titles into sets of words
    applied_words = set(applied_clean.split())
    suggested_words = set(suggested_clean.split())
    
    # Check if there's an overlap in the words (considering both titles as sets)
    return not applied_words.isdisjoint(suggested_words)

def display_tips(processed_data, missing_fields):
    # Unpack data
    na_count = processed_data.get('na_count', 0)
    suggested_category = processed_data.get('suggested_category', "N/A")
    applied_profile = processed_data.get('applied_profile', "N/A")
    Recommended_Additional_Skills = processed_data.get("Recommended_Additional_Skills", [])

    # Check for missing date fields
    date_fields = ["Start_Date", "End_Date", "Graduation_Date"]
    missing_dates = sum(
        1 for field in missing_fields
        if any(date_key in field for date_key in date_fields)
    )



    # Calculate final score
    base_score = processed_data.get('resume_score', 0)
    final_score = max(0, base_score - (na_count * 2 + len(Recommended_Additional_Skills) * 1.5))

    with st.container():
        st.markdown("""<hr style="height:2px; border:none;  background-color: #01285EFF;  margin-bottom: 1rem;">""", unsafe_allow_html=True)

        st.markdown('''<div style='text-align: center; margin-bottom: -1rem;'><h4 style='color: #1d3557;'>Resume Tips & Ideas 💡</h4></div>''', 
                    unsafe_allow_html=True)
        st.markdown(f"""<div style="text-align: center; margin-top: -0.7rem;">
                        <h3 style="color: #1d3557; margin-bottom: 1rem;">{final_score}/100</h3>
                        <p style="color: #1970A6FF; font-size: 0.9rem; margin-top: -1.8rem;margin-left: -1.5rem;">Resume Score</p>
                    </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div style="text-align: center; margin-top: 10px;">
                        <p style="color: #60686DFF; font-size: 0.7rem; margin-top: -25px;text-align: center;">( The score is calculated based on the content of your Resume.)</p>
                    </div>""", unsafe_allow_html=True)

        # Show either success message or NA count warning
        if na_count > 0:
            st.markdown(f"""
                <div style="padding: 10px; margin-top: 0.7rem; margin-bottom: 0.5rem; border-radius: 25px; 
                            text-align: center; overflow: hidden;">
                    <div style="padding: 10px; background: linear-gradient(to right, #bd1f36, #FF3A2CFF); 
                                border-radius: 25px; color: #EED5D5FF;">
                        ⚠️ Found {na_count} missing fields. Include these fields for ATS compatibility.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="padding: 10px; margin-top: 0.7rem; margin-bottom: 0.5rem; border-radius: 25px; 
                            text-align: center; overflow: hidden;">
                    <div style="padding: 10px; background: linear-gradient(to right, #2b9348, #54FF0BFF); 
                                border-radius: 25px;color:#143601;">
                        ✅ Congratulations! Your resume is ATS compatible!
                    </div>
                </div>
            """, unsafe_allow_html=True)

        if suggested_category and applied_profile and not profiles_match(applied_profile, suggested_category):
            st.markdown(f"""
                <div style="padding: 10px; margin-top: 0.7rem; margin-bottom: 0.5rem; border-radius: 25px; 
                            text-align: center; overflow: hidden;">
                    <div style="padding: 10px; background: linear-gradient(to right, #bd1f36, #FF3A2CFF); 
                                border-radius: 25px; color: #EED5D5FF;">
                        🎯 Profile mismatch: Applied for "{applied_profile}" but suggested "{suggested_category}"
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="padding: 10px; margin-top: 0.7rem; margin-bottom: 0.5rem; border-radius: 25px; 
                            text-align: center; overflow: hidden;">
                    <div style="padding: 10px; background: linear-gradient(to right, #2b9348, #54FF0BFF); 
                                border-radius: 25px; color: #143601;">
                        ✅ Congratulations! Your Resume keywords match with the Suggested Resume Category!
                    </div>
                </div>
            """, unsafe_allow_html=True)


            # Show warning only if there are actual missing dates
            if missing_dates > 0:
                st.markdown(f"""
                    <div style="padding: 10px; margin-top: 0.7rem; margin-bottom: 2rem; border-radius: 25px; 
                                text-align: center; overflow: hidden;">
                        <div style="padding: 10px; background: linear-gradient(to right, #bd1f36, #FF3A2CFF); 
                                    border-radius: 25px;color: #EED5D5FF;">
                            📅 Found {missing_dates} date fields missing. Use <strong>(Month YYYY)</strong> or <strong>(mm/yyyy)</strong> format.
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="padding: 10px; margin-top: 0.7rem; margin-bottom: 2rem; border-radius: 25px; 
                                text-align: center; overflow: hidden;">
                        <div style="padding: 10px; background: linear-gradient(to right, #2b9348, #54FF0BFF); 
                                    border-radius: 25px;color: #EED5D5FF;">
                            📅 Found no missing date fields.
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Course recommendations
        course_list = []
        if applied_profile:
            if any(kw in applied_profile.lower() for kw in ["data", "science", "machine learning"]):
                course_list = ds_course
            elif "web" in applied_profile.lower():
                course_list = web_course
            elif "android" in applied_profile.lower():
                course_list = android_course
            elif "ios" in applied_profile.lower():
                course_list = ios_course
            elif "qa" in applied_profile.lower():
                course_list = qa_course
            elif "software" in applied_profile.lower():
                course_list = software_dev_course
            elif any(kw in applied_profile.lower() for kw in ["ui", "ux", "design"]):
                course_list = uiux_course

        col1, col2, col3, col4 = st.columns([0.2, 1, 0.2, 1])

        with col2:
            if course_list:
                st.markdown('''<div style="margin-top:1rem; margin-bottom:-1.8rem;">
                                <h5 style="color: #1d3557;">Recommended Courses & Certifications 📚</h5>
                            </div>''', unsafe_allow_html=True)
                courses_recommendation(course_list)
                st.caption("Take these Courses & Certifications for skill development")
            else:  # Show message when no courses are available for the profile
                
                st.markdown(f'''<div style="margin-top:1rem; margin-bottom:0.5rem;">
                                <h5 style="color: #1d3557;">Recommended Learning Resources </h5>
                            </div>''', unsafe_allow_html=True)
                st.markdown(f"""
                <div>
                    No specific courses found for <strong>{applied_profile}</strong>. Consider these general resources:
                    <br><br>
                    🌐 Explore platforms like:
                    <ul>
                        <li><a href="https://www.coursera.org/" target="_blank">Coursera</a> - Professional certificates</li>
                        <li><a href="https://www.linkedin.com/learning/" target="_blank">LinkedIn Learning</a> - Skill development</li>
                        <li><a href="https://www.udemy.com/" target="_blank">Udemy</a> - Practical project-based courses</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        with col4:
            if Recommended_Additional_Skills:
                st.markdown('''<div style="margin-top:0.4rem; padding:10px;">
                                <h5 style="color: #1d3557;">Recommended Additional Skills 🛠️</h5>
                            </div>''', unsafe_allow_html=True)
                for skill in Recommended_Additional_Skills:
                    st.markdown(f"🪛 &nbsp;&nbsp;&nbsp;{skill}")
                st.caption("Adding these skills to your resume will boost your chances of getting a job.")

        st.markdown("""<hr style="height:2px; border:none;  background-color: #01285EFF;  margin: 2rem 0;">""", unsafe_allow_html=True)

        # Video recommendation
        st.markdown('''<div style='text-align: center; margin-top: -1rem;'><h4 style='color: #1d3557;'>Bonus Video for Resume Writing🎬</h4></div>''', 
                    unsafe_allow_html=True)
        fetch_yt_video()
def display_footer():
    st.markdown("""
    <style>

        .footer a {
        color:#1A4562D1;

        margin-left: 5px;
    }

    .footer {
    position:fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #112F615B; /* Semi-transparent dark blue */
    text-align: center;
    display: flex;
    justify-content: center;
    color:#FFFFFFFF;
    backdrop-filter: blur(7rem);
    }
    </style>
    
    <div class="footer">
        © 2025 Resume Analyzer By Agrani Chapagain | Supervision: Mr. Sandeep Gautam | Apex College
        <div style="font-size: 1rem;">
            | Gmail: 
            <a href="https://mail.google.com/mail/?view=cm&fs=1&to=agrani58@gmail.com">agrani58@gmail.com</a>
        </div>
    </div>
    """, unsafe_allow_html=True)