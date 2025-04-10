import os
import re
import string
import docx2txt
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Get stop words
stop_words = set(stopwords.words('english'))

# Add domain-specific stop words
domain_stop_words = {'resume', 'cv', 'curriculum', 'vitae', 'name', 'email', 'phone', 'address', 'experience'}
stop_words.update(domain_stop_words)

def preprocess_text(text):
    """Preprocess text for better similarity matching"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stop words and lemmatize
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    
    # Rejoin
    processed_text = ' '.join(processed_tokens)
    
    return processed_text

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file"""
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    """Extract text from a TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            print(f"Error extracting text from TXT with latin-1 encoding: {e}")
            return ""
    except Exception as e:
        print(f"Error extracting text from TXT: {e}")
        return ""

def extract_text(file_path):
    """Extract text from a file based on its extension"""
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        return ""

def calculate_similarity(job_description, resume_text):
    """Calculate cosine similarity between job description and resume"""
    if not job_description or not resume_text:
        return 0
    
    # Preprocess texts
    processed_job = preprocess_text(job_description)
    processed_resume = preprocess_text(resume_text)
    
    # Vectorize
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([processed_job, processed_resume])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Scale to 0-100
        similarity_score = round(similarity * 100, 2)
        
        return similarity_score
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0

def extract_email(text):
    """Extract email from text using regex"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None 