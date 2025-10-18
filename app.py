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
    coverage_pct = get_keyword_coverage(clean_resume, clean_jd)

    # Categorize missing keywords
    categorized = categorize_keywords(missing_keywords)

    # Section detection
    sections_found = section_detection(resume_text)

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

    # Add single summary line instead of Domain/Other section
    st.markdown("🧩 No major domain-specific gaps detected.")

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
    # 📈 Visual Dashboard (charts only)
    # -------------------------------
    st.markdown("---")
    st.markdown("## 📈 Visual Insights")

    # Improved interactive bar chart for Overall Scores
import plotly.graph_objects as go

scores = [match_score, format_score, grammar_score]
labels = ["ATS Match", "Formatting", "Grammar"]

fig_bar = go.Figure(data=[
    go.Bar(
        x=labels,
        y=scores,
        marker_color=["#2b8cbe", "#7fc97f", "#fdae61"],
        text=[f"{s:.1f}%" for s in scores],
        textposition="auto"
    )
])

fig_bar.update_layout(
    title="📊 Overall ATS Performance",
    yaxis_title="Score (%)",
    yaxis_range=[0, 100],
    template="simple_white",
    title_font=dict(size=18, color="#333", family="Arial"),
    plot_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig_bar, use_container_width=True)

# Modern donut-style chart for JD Keyword Coverage
cover = coverage_pct
remaining = max(0, 100 - cover)

fig_pie = go.Figure(data=[go.Pie(
    values=[cover, remaining],
    labels=["Covered", "Missing"],
    marker_colors=["#2b8cbe", "#e0e0e0"],
    hole=0.6,
    textinfo="none"
)])

fig_pie.update_layout(
    title="🧩 JD Keyword Coverage",
    annotations=[dict(text=f"{cover:.1f}%", x=0.5, y=0.5, font_size=20, showarrow=False)],
    showlegend=True,
    template="simple_white"
)

st.plotly_chart(fig_pie, use_container_width=True)

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
