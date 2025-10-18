import re
import PyPDF2
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import io
from collections import Counter
from wordcloud import WordCloud
from PIL import Image

# Ensure NLTK stopwords
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
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
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
            if para.text:
                text += para.text + "\n"
    except Exception as e:
        text = "Error reading DOCX: " + str(e)
    return text


# -------------------------------
# 3️⃣ Clean the text (remove symbols, stopwords)
# -------------------------------
def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    tokens = [word for word in text.split() if word not in stop_words and len(word) > 1]
    return " ".join(tokens)


# -------------------------------
# 4️⃣ Calculate ATS match score (using TF-IDF)
# -------------------------------
def calculate_similarity(resume_text, job_description):
    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(vectors)[0][1]
        return round(float(similarity * 100), 2)
    except Exception:
        return 0.0


# -------------------------------
# 5️⃣ Find missing keywords
# -------------------------------
def find_missing_keywords(resume_text, job_description, top_n=50):
    resume_words = set(resume_text.split())
    jd_words = Counter(job_description.split())
    # Consider JD words longer than 3 chars and not stopwords
    jd_keywords = [w for w, _ in jd_words.most_common() if len(w) > 3 and w not in stop_words]
    missing = [w for w in jd_keywords if w not in resume_words]
    return missing[:top_n]


# -------------------------------
# 6️⃣ Formatting check (simple)
# -------------------------------
def check_formatting(resume_text):
    score = 100
    feedback = []

    if not resume_text or len(resume_text) < 400:
        score -= 25
        feedback.append("Resume seems short. Consider adding more content and details.")

    low = resume_text.lower()
    if "education" not in low:
        score -= 10
        feedback.append("Missing Education section.")
    if "experience" not in low and "work experience" not in low:
        score -= 10
        feedback.append("Missing Experience section.")
    if "skills" not in low:
        score -= 10
        feedback.append("Missing Skills section.")

    return max(score, 0), feedback


# -------------------------------
# 7️⃣ Grammar/readability score (simple proxy)
# -------------------------------
def grammar_check_score(text):
    if not text:
        return 0.0
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    score = 100 - abs(avg_length - 15) * 2  # ideal avg sentence length ~15 words
    return max(min(round(score, 2), 100), 0)


# -------------------------------
# 8️⃣ Skill categorization (technical, soft, domain)
# -------------------------------
# Lightweight predefined lists. You can expand these lists over time.
TECHNICAL_SKILLS = {
    "python", "java", "c++", "c#", "sql", "nosql", "mongodb", "postgresql", "mysql",
    "tensorflow", "pytorch", "keras", "sklearn", "pandas", "numpy", "r", "excel",
    "tableau", "powerbi", "aws", "azure", "gcp", "docker", "kubernetes", "git",
    "html", "css", "javascript", "react", "nodejs", "django", "flask", "spark", "hadoop"
}

SOFT_SKILLS = {
    "communication", "teamwork", "leadership", "problem-solving", "adaptability",
    "time-management", "creativity", "critical-thinking", "collaboration", "presentation",
    "mentoring", "coaching", "organization", "interpersonal", "negotiation"
}

def categorize_keywords(keywords):
    technical = []
    soft = []
    domain = []
    for k in keywords:
        kk = k.lower()
        if kk in TECHNICAL_SKILLS:
            technical.append(k)
        elif kk in SOFT_SKILLS:
            soft.append(k)
        else:
            domain.append(k)
    return {"technical": technical, "soft": soft, "domain": domain}


# -------------------------------
# 9️⃣ Keyword coverage percent
# -------------------------------
def get_keyword_coverage(resume_text, job_description):
    resume_words = set(resume_text.split())
    jd_words = [w for w in job_description.split() if len(w) > 3 and w not in stop_words]
    if not jd_words:
        return 100.0
    covered = sum(1 for w in set(jd_words) if w in resume_words)
    pct = (covered / len(set(jd_words))) * 100
    return round(pct, 2)


# -------------------------------
# 🔟 Wordcloud generation helper
# -------------------------------
def generate_wordcloud_image(word_counts, width=600, height=400):
    # word_counts: list of (word, count) OR list of words
    if isinstance(word_counts, dict):
        freqs = word_counts
    elif isinstance(word_counts, list):
        # list of words -> build counts
        freqs = Counter(word_counts)
    else:
        # if a list of tuples
        try:
            freqs = dict(word_counts)
        except Exception:
            freqs = {}

    if not freqs:
        freqs = {"empty": 1}

    wc = WordCloud(width=width, height=height, background_color="white", collocations=False)
    wc.generate_from_frequencies(freqs)
    img = wc.to_image()
    # Convert to in-memory bytes for Streamlit
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# -------------------------------
# 1️⃣1️⃣ Section detection (simple)
# -------------------------------
def section_detection(text):
    low = (text or "").lower()
    sections = {
        "summary": bool(re.search(r'\bsummary\b|\bprofile\b|\boverview\b', low)),
        "experience": bool(re.search(r'\bexperience\b|\bwork experience\b|\bprofessional experience\b', low)),
        "projects": bool(re.search(r'\bprojects\b|\bproject\b', low)),
        "education": bool(re.search(r'\beducation\b|\bdegree\b|\buniversity\b|\bcollege\b', low)),
        "skills": bool(re.search(r'\bskills\b|\btechnical skills\b|\bprofessional skills\b', low)),
        "certifications": bool(re.search(r'\bcertif|certificate|licenses\b', low))
    }
    return sections


# -------------------------------
# 1️⃣2️⃣ Top N words (for wordcloud input)
# -------------------------------
def top_n_words(text, n=100):
    words = [w for w in (text or "").split() if len(w) > 2 and w not in stop_words]
    counts = Counter(words)
    top = counts.most_common(n)
    # return dict for the wordcloud generator
    return dict(top)
