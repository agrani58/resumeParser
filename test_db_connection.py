import nltk
import sys
nltk.download('stopwords')  # Downloads stopwords corpus
from nltk.corpus import stopwords
print(stopwords.words('english')[:10])  # Test if stopwords are accessible
print(sys.executable)