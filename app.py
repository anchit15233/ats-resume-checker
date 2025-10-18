import streamlit as st
from helper_functions import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    calculate_similarity,
    find_missing_keywords,
    check_formatting,
    grammar_check_score,
    categorize_keywords,
    get_keyword_coverage,
    generate_wordcloud_image,
    section_detection,
    top_n_words
)
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

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
st.title("📄 ATS Resume Checker — Professional Dashboard")
st.markdown("---")
st.markdown("### 🚀 Paste a Job Description and upload a Resume (PDF / DOCX) to get an ATS-ready analysis")

# -------------------------------
# 🧾 Inputs
# -------------------------------
uploaded_file = st.file_uploader("📂 Upload your Resume", type=["pdf", "docx"])
job_description = st.text_area("💼 Paste the Job Description Here", height=220)

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

    # Keyword coverage for pie/chart
    coverage_pct = get_keyword_coverage(clean_resume, clean_jd)  # 0-100

    # Categorize missing keywords
    categorized = categorize_keywords(missing_keywords)

    # Section detection
    sections_found = section_detection(resume_text)

    # Top words for wordclouds
    resume_top = top_n_words(clean_resume, n=80)
    jd_top = top_n_words(clean_jd, n=80)

    # -------------------------------
    # 📊 Results Section (Professional layout)
    # -------------------------------
    st.markdown("---")
    st.markdown("## 📊 ATS Match Results")

    # Top summary cards
    col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.2, 1])
    with col1:
        st.subheader("🔎 ATS Match")
        st.metric(label="Match Score", value=f"{match_score} %")
        st.progress(int(match_score))
    with col2:
        st.subheader("🧩 Formatting")
        st.metric(label="Formatting Score", value=f"{format_score} %")
        st.progress(int(format_score))
    with col3:
        st.subheader("✍️ Grammar")
        st.metric(label="Grammar Score", value=f"{grammar_score} %")
        st.progress(int(grammar_score))
    with col4:
        st.subheader("📄 Resume")
        st.write(f"**Words:** {word_count}")
        st.write(f"**Keyword Coverage:** {coverage_pct:.1f}%")

    # Recommendation
    st.markdown("---")
    st.markdown("### ✅ High-level Recommendation")
    if match_score > 70:
        st.success("Strong match! Your resume aligns well with this job description.")
    elif match_score > 40:
        st.warning("Moderate match — consider adding more role-specific keywords and sections.")
    else:
        st.error("Low match. Tailor your resume for this role and add missing skills or sections.")

    # -------------------------------
    # 🧩 Missing Keywords — categorized
    # -------------------------------
    st.markdown("---")
    st.markdown("## 🧠 Missing Keywords (Skill Gap)")

    tech = categorized.get("technical", [])
    soft = categorized.get("soft", [])
    domain = categorized.get("domain", [])

    st.markdown("### 🔧 Technical Skills")
    if tech:
        st.write(", ".join(tech))
    else:
        st.success("No major technical gaps detected.")

    st.markdown("### 💬 Soft Skills")
    if soft:
        st.write(", ".join(soft))
    else:
        st.success("Soft skills covered.")

    st.markdown("### 🏢 Domain / Other Keywords")
    if domain:
        st.write(", ".join(domain))
    else:
        st.success("Domain keywords covered or none missing.")

    # -------------------------------
    # 🧾 Section Breakdown (visual checklist)
    # -------------------------------
    st.markdown("---")
    st.markdown("## 🧾 Resume Section Breakdown")
    cols = st.columns(3)
    keys = ["summary", "experience", "projects", "education", "skills", "certifications"]
    icons = {True: "✅", False: "⚠️"}

    for i, k in enumerate(keys):
        col = cols[i % 3]
        found = sections_found.get(k, False)
        label = k.capitalize()
        if found:
            col.success(f"{icons[True]} {label}")
        else:
            col.warning(f"{icons[False]} {label}")

    # Show formatting feedback details
    if format_feedback:
        st.markdown("**Formatting Feedback:**")
        for tip in format_feedback:
            st.info(f"• {tip}")

    # -------------------------------
    # 📈 Visual Dashboard (charts & wordclouds)
    # -------------------------------
    st.markdown("---")
    st.markdown("## 📈 Visual Insights")

    # Bar chart for three scores
    fig1, ax1 = plt.subplots(figsize=(6, 3))
    scores = [match_score, format_score, grammar_score]
    labels = ["Match", "Formatting", "Grammar"]
    bar_colors = ["#2b8cbe", "#7fc97f", "#fdae61"]  # professional tri-color
    ax1.bar(labels, scores, color=bar_colors)
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("Score (%)")
    ax1.set_title("Overall Scores")
    for i, v in enumerate(scores):
        ax1.text(i, v + 1, f"{v}%", ha='center')
    st.pyplot(fig1)

    # Pie chart for keyword coverage
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    cover = coverage_pct
    remaining = max(0, 100 - cover)
    ax2.pie([cover, remaining], labels=[f"Covered {cover:.1f}%", f"Missing {remaining:.1f}%"],
            autopct='%1.1f%%', colors=["#2b8cbe", "#e0e0e0"])
    ax2.set_title("JD Keyword Coverage")
    st.pyplot(fig2)

    # Wordclouds side-by-side (✅ fixed for deprecation)
    wc_col1, wc_col2 = st.columns(2)
    with wc_col1:
        st.subheader("Resume — Top Words")
        img_res = generate_wordcloud_image(resume_top)
        st.image(img_res, use_container_width=True)

    with wc_col2:
        st.subheader("Job Description — Top Words")
        img_jd = generate_wordcloud_image(jd_top)
        st.image(img_jd, use_container_width=True)

    # -------------------------------
    # ✅ Summary
    # -------------------------------
    st.markdown("---")
    st.markdown("## 📌 Summary & Next Steps")
    st.write("- Try adding missing technical keywords into your Skills and Experience bullets.")
    st.write("- Expand or add Projects if missing — highlight measurable outcomes.")
    st.write("- Re-run and check improvements (you can upload an updated resume).")

else:
    st.info("👆 Please upload your resume and paste a job description to begin.")


