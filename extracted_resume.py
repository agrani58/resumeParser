from pdfminer.high_level import extract_text
from json_helper import InputData as input

# Function to extract text from the resume
def extract_text_from_pdf(save_dir):
    return extract_text(save_dir)

# Provide the path to your resume
resume_path = r"Uploaded_Resumes"


# Extract text from the resume
text = extract_text_from_pdf(resume_path)

# Initialize the LLM
llm = input.llm()

# Check if the LLM was initialized properly
if llm is not None:
    print("Model initialized successfully")
else:
    print("Model initialization failed")

# Pass the extracted text to the LLM for processing
data = llm.invoke(input.input_data(text))

# Print the parsed data (adjust the output according to the model's response structure)
print(data)
