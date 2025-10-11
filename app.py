import streamlit as st
from helper_functions import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    calculate_similarity,
    find_missing_keywords,
    check_formatting,
    grammar_check_score
)

# -------------------------------
# ⚙️ App Configuration
# -------------------------------
st.set_page_config(page_title="ATS Resume Checker", layout="wide")

# -------------------------------
# 💬 Sidebar
# -------------------------------
with st.sidebar:
    st.title("ℹ️ About")
    st.info(
        "This ATS Resume Checker compares your resume with a job description "
        "and provides insights on keyword match, formatting, and readability."
    )
    

# -------------------------------
# 🏁 Title & Description
# -------------------------------
st.title("📄 ATS Resume Checker")
st.markdown("---")
st.markdown("### 🚀 Check your resume compatibility with any job description instantly!")

# -------------------------------
# 🧾 Inputs
# -------------------------------
uploaded_file = st.file_uploader("📂 Upload your Resume", type=["pdf", "docx"])
job_description = st.text_area("💼 Paste the Job Description Here", height=200)

if uploaded_file and job_description:
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_name.endswith(".docx"):
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload a PDF or DOCX.")
        st.stop()

    # Clean text
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(job_description)

    # -------------------------------
    # 🔍 Calculate Scores
    # -------------------------------
    match_score = calculate_similarity(clean_resume, clean_jd)
    missing_keywords = find_missing_keywords(clean_resume, clean_jd)
    format_score, format_feedback = check_formatting(resume_text)
    grammar_score = grammar_check_score(resume_text)
    word_count = len(resume_text.split())

    # -------------------------------
    # 📊 Results Section
    # -------------------------------
    st.markdown("---")
    st.markdown("## 📊 ATS Match Results")

    st.write(f"**ATS Match Score:** {match_score}%")
    st.progress(int(match_score))

    st.write(f"**Formatting Score:** {format_score}%")
    st.progress(int(format_score))

    st.write(f"**Grammar / Readability Score:** {grammar_score}%")
    st.progress(int(grammar_score))

    st.write(f"**Word Count:** {word_count}")

    # -------------------------------
    # 🧠 Missing Keywords
    # -------------------------------
    st.markdown("---")
    st.markdown("## 🧠 Missing Keywords")
    if missing_keywords:
        st.warning(", ".join(missing_keywords))
    else:
        st.success("All key terms from the job description seem to be covered!")

    # -------------------------------
    # 🧩 Formatting Feedback
    # -------------------------------
    st.markdown("---")
    st.markdown("## 🧩 Formatting Feedback")
    if format_feedback:
        for tip in format_feedback:
            st.info(f"• {tip}")
    else:
        st.success("Good formatting! Key sections found.")

    # -------------------------------
    # ✅ Summary
    # -------------------------------
    st.markdown("---")
    st.markdown("## ✅ Summary")
    if match_score > 70:
        st.success("Strong match! Your resume aligns well with this job description.")
    elif match_score > 40:
        st.warning("Moderate match — consider adding more role-specific keywords.")
    else:
        st.error("Low match. Try tailoring your resume for this specific role.")

else:
    st.info("👆 Please upload your resume and paste a job description to begin.")

