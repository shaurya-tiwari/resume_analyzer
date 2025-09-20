import streamlit as st
import pdfplumber
import docx
from utils import (
    clean_text,
    detect_resume_sections,
    calculate_category_scores,
    ats_verdict,
    recommendation_list,
    summarize_strength_gaps,
    analyze_resume_quality_pplx,   # switched to pplx
    generate_resume_booster_pplx,  # switched to pplx
    semantic_skill_match,          # if still defined in utils
)
from skills_db import ALL_SKILLS


# -------------------------------
# File readers
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return "\n".join([p.text for p in doc.paragraphs])


# -------------------------------teh thing which are sam to me that 
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyzer — Pro Edition")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Upload Resume")
    resume_file = st.file_uploader("PDF or DOCX", type=["pdf", "docx"])
with col2:
    st.subheader("Paste Job Description")
    job_description = st.text_area("Enter JD here...", height=200)

resume_text = ""
if resume_file:
    if resume_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(resume_file)
    else:
        resume_text = extract_text_from_docx(resume_file)

# -------------------------------
# Run Analysis
# -------------------------------
if st.button("🔍 Analyze", use_container_width=True):
    if not resume_text or not job_description.strip():
        st.warning("Please upload resume + job description.")
        st.stop()

    # Extract sections
    sections = detect_resume_sections(resume_text)
    resume_tokens = clean_text(resume_text)
    jd_tokens = clean_text(job_description)

    # Skills (semantic matching if defined, else fallback to simple overlap)
    try:
        matched, missing = semantic_skill_match(resume_text, job_description)
    except Exception:
        matched, missing = set(resume_tokens) & set(jd_tokens), set(jd_tokens) - set(resume_tokens)

    resume_skills = matched
    jd_skills = matched.union(missing)  # JD expects both

    # Scores
    scores = calculate_category_scores(resume_skills, jd_skills)
    scores["matched_flat"] = list(matched)
    scores["missing_flat"] = list(missing)
    overall = scores["overall_score"]
    verdict = ats_verdict(overall, scores["missing_flat"])

    # -------------------------------
    # UI Output
    # -------------------------------
    st.markdown("### 📊 Job Fit Overview")
    st.progress(int(overall))
    st.success(f"Overall Match: {overall:.1f}% — {verdict}")

    st.markdown("### 💡 Summary")
    st.write(summarize_strength_gaps(scores))

    st.markdown("### 📝 Action Items")
    for rec in recommendation_list(
        scores["missing_flat"],
        clean_text(sections.get("skills", "")),
        clean_text(sections.get("projects", "")),
        clean_text(sections.get("experience", "")),
    ):
        st.write("- " + rec)

    # ✅ Perplexity Booster
    st.subheader("🚀 AI Resume Booster (JD Specific)")
    booster_text = generate_resume_booster_pplx(
        missing_skills=scores["missing_flat"],
        job_description=job_description,
        matched_skills=scores.get("matched_flat", []),
        overall_score=overall,
    )
    st.info(booster_text)

    # ✅ Perplexity Resume Quality
    st.subheader("📊 Resume Quality (General ATS Check)")
    quality_text = analyze_resume_quality_pplx(resume_text)
    st.info(quality_text)
