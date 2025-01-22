from langchain_community.llms import Ollama

# Define JSON content template for resume data
json_content = """{
    "name": "",
    "email": "",
    "phone_1": "",
    "phone_2": "",
    "address": "",
    "city": "",
    "linkedin": "",
    "professional_experience_in_years": "",
    "highest_education": "",
    "is_fresher": "yes/no",
    "is_student": "yes/no",
    "skills": ["", ""],
    "applied_for_profile": "",
    "education": [
        {
            "institute_name": "",
            "year_of_passing": "",
            "score": ""
        },
        {
            "institute_name": "",
            "year_of_passing": "",
            "score": ""
        }
    ],
    "professional_experience": [
        {
            "organisation_name": "",
            "duration": "",
            "profile": ""
        },
        {
            "organisation_name": "",
            "duration": "",
            "profile": ""
        }
    ]
}"""

class InputData:
    @staticmethod
    def input_data(cleaned_text):
        """
        Prepares the input prompt for the model to extract the information and return the JSON formatted result.
        This method is static because it doesn't need to operate on an instance of InputData.
        """
        input_prompt = f"""
        Extract relevant information from the following resume text and fill the provided JSON template. 
        Ensure all keys in the template are present in the output, even if the value is empty or unknown. 
        If a specific piece of information is not found in the text, use 'Not provided' as the value.

        Resume text:
        {cleaned_text}

        JSON template:
        {json_content}

        Instructions:
        1. Carefully analyze the resume text.
        2. Extract relevant information for each field in the JSON template.
        3. If a piece of information is not explicitly stated, make a reasonable inference based on the context.
        4. Ensure all keys from the template are present in the output JSON.
        5. Format the output as a valid JSON string.

        Output the filled JSON template only, without any additional text or explanations.
        """
        
        return input_prompt
    
    @staticmethod
    def llm():
        """
        Initializes and returns the Ollama LLM model.
        """
        llm = Ollama(model="llama3")
        return llm
