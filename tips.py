# from json_file import display_in_container, display_parsed_data
# from libraries import *  # Ensure you really need to import everything

# def courses_recommendation(course_list, parsed_data):
#     # Get the recommended values from parsed_data using our helper function
#     suggested_category, recommended_skills = display_parsed_data(parsed_data)
    
#     st.markdown(
#         '''<div style='margin-top: 20px; text-align: center;'> 
#                 <h5 style='color: #1d3557;'>Resume Tips & Tricks</h5>
#             </div>''',
#         unsafe_allow_html=True
#     )
    
#     # Use the retrieved values in display_in_container
#     display_in_container(f"🌟 Recommended Skills for {suggested_category}", recommended_skills)
#     st.caption("Adding these skills to resume will boost your chance of getting a job")
    
#     c = 0
#     rec_course = []
#     no_of_reco = st.slider('Choose Number of Courses You want to be Recommended', 1, 10, 5)
#     random.shuffle(course_list)
#     for c_name, c_link in course_list:
#         c += 1
#         st.markdown(f'({c}) [{c_name}]({c_link})')
#         rec_course.append(c_name)
#         if c == no_of_reco:
#             break
#     return rec_course

# # Example usage:
# # Assume you have resume_text from somewhere and you obtain parsed_data as follows:
# # parsed_data = resume_details(resume_text)
# # courses_recommendation(course_list, parsed_data)
