import re
import PyPDF2
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import nltk

# Download stopwords if not already present
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

# -------------------------------
# 1️⃣ Extract text from PDF
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    except Exception as e:
        text = "Error reading PDF: " + str(e)
    return text


# -------------------------------
# 2️⃣ Extract text from DOCX
# -------------------------------
def extract_text_from_docx(uploaded_file):
    text = ""
    try:
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        text = "Error reading DOCX: " + str(e)
    return text


# -------------------------------
# 3️⃣ Clean the text (remove symbols, stopwords)
# -------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = [word for word in text.split() if word not in stop_words]
    return " ".join(tokens)


# -------------------------------
# 4️⃣ Calculate ATS match score (using TF-IDF)
# -------------------------------
def calculate_similarity(resume_text, job_description):
    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(vectors)[0][1]
        return round(similarity * 100, 2)
    except Exception as e:
        return 0


# -------------------------------
# 5️⃣ Find missing keywords
# -------------------------------
def find_missing_keywords(resume_text, job_description):
    resume_words = set(resume_text.split())
    jd_words = set(job_description.split())

    # Filter short and common words
    jd_keywords = [w for w in jd_words if len(w) > 3 and w not in stop_words]
    missing = [w for w in jd_keywords if w not in resume_words]

    # Keep top unique 20
    return missing[:20]


# -------------------------------
# 6️⃣ Formatting check (simple)
# -------------------------------
def check_formatting(resume_text):
    score = 100
    feedback = []

    # Very naive checks
    if len(resume_text) < 500:
        score -= 20
        feedback.append("Resume seems too short. Consider adding more content.")

    if "education" not in resume_text.lower():
        score -= 10
        feedback.append("Missing Education section.")

    if "experience" not in resume_text.lower():
        score -= 10
        feedback.append("Missing Experience section.")

    if "skills" not in resume_text.lower():
        score -= 10
        feedback.append("Missing Skills section.")

    return max(score, 0), feedback


# -------------------------------
# 7️⃣ Grammar/readability score (simple proxy)
# -------------------------------
def grammar_check_score(text):
    sentences = re.split(r'[.!?]', text)
    avg_length = sum(len(s.split()) for s in sentences if len(s) > 0) / max(len(sentences), 1)
    score = 100 - abs(avg_length - 15) * 2  # ideal avg sentence length ~15 words
    return max(min(round(score, 2), 100), 0)

