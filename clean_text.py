import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Download required NLTK datasets (run this once if you haven't already)
nltk.download('punkt')
nltk.download('stopwords')

def clean_text(resume_text):
    """
    Cleans the extracted resume text by:
    - Removing stopwords
    - Removing unwanted characters (e.g., punctuation, newlines)
    - Converting to lowercase
    - Keeping necessary punctuation for emails, phone numbers, and relevant data
    """
    # Define stopwords
    stop_words = set(stopwords.words('english'))
    
    # Remove unwanted characters like newlines and extra spaces (correcting the regex)
    resume_text = re.sub(r'[^\w\s@.,-]', '', resume_text)
    
    # Tokenize the input text
    word_tokens = word_tokenize(resume_text)
    
    # Filter out stopwords and non-alphanumeric words
    filtered_words = [word.lower() for word in word_tokens if word.lower() not in stop_words]
    
    # Join the filtered words back into a string
    cleaned_text = ' '.join(filtered_words)  # Join the filtered words into a sentence
    
    return cleaned_text

