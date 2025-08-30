import streamlit as st
import pdfplumber
import docx
import re

from utils import (
    clean_text,
    detect_resume_sections,
    nlp_extract_keywords,
    expand_with_synonyms,
    extract_skills_exact,
    calculate_category_scores,
    ats_verdict,
    recommendation_list,
    summarize_strength_gaps,
)
from skills_db import TECH_SKILLS, SOFT_SKILLS, DEVOPS_CLOUD_SKILLS, ALL_SKILLS


# -------------------------------
# File readers
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    """Extract full text from a PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(uploaded_file):
    """Extract full text from a DOCX using python-docx."""
    doc = docx.Document(uploaded_file)
    return "\n".join([p.text for p in doc.paragraphs])


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyzer — Pro Edition")

left, right = st.columns(2)
with left:
    st.subheader("Upload Resume")
    resume_file = st.file_uploader("PDF or DOCX", type=["pdf", "docx"])

with right:
    st.subheader("Paste Job Description")
    job_description = st.text_area(
        "Enter JD here...",
        height=220,
        placeholder="e.g., We need experience with containerization, relational databases, React, and communication skills...",
    )

with st.expander("⚙️ Options"):
    show_previews = st.checkbox("Show extracted text previews", value=False)
    min_keyphrases = st.slider(
        "Max keyphrases extracted from JD (NLP)",
        min_value=5,
        max_value=30,
        value=12,
        step=1,
    )
    tech_w, soft_w, devops_w = 60, 40, 20  # fixed weights per your requirement

# -------------------------------
# Read resume text
# -------------------------------
resume_text = ""
if resume_file is not None:
    if resume_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(resume_file)
    elif (
        resume_file.type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        resume_text = extract_text_from_docx(resume_file)

# -------------------------------
# Analyze
# -------------------------------
if st.button("🔍 Analyze", use_container_width=True):
    if not resume_text or not job_description.strip():
        st.warning("Please upload a resume and paste a job description.")
        st.stop()

    # 1) Clean + Section detection
    sections = detect_resume_sections(resume_text)
    resume_tokens_all = clean_text(resume_text)
    jd_tokens_all = clean_text(job_description)

    # 2) NLP keyword extraction from JD (spaCy → fallback TF-IDF)
    jd_keyphrases = nlp_extract_keywords(job_description, top_k=min_keyphrases)
    # Expand JD phrases with synonyms to catch semantic intent
    jd_expanded = expand_with_synonyms(jd_keyphrases)

    # 3) Skill extraction (exact, with short-skill context rules)
    resume_skills_all = extract_skills_exact(resume_tokens_all, ALL_SKILLS)
    jd_skills_all = extract_skills_exact(jd_tokens_all, ALL_SKILLS)

    # Section-wise skills (helps in suggestions like "add project for SQL")
    skills_section = extract_skills_exact(
        clean_text(sections.get("skills", "")), ALL_SKILLS
    )

    projects_section = extract_skills_exact(
        clean_text(sections.get("projects", "")), ALL_SKILLS
    )

    experience_section = extract_skills_exact(
        clean_text(sections.get("experience", "")), ALL_SKILLS
    )

    # 4) Category-wise scoring + overall
    scores = calculate_category_scores(
        resume_skills=resume_skills_all,
        jd_skills=jd_skills_all,
        tech_weight=tech_w,
        soft_weight=soft_w,
        devops_weight=devops_w,
    )
    overall_pct = scores["overall_score"]
    verdict = ats_verdict(overall_pct, scores["missing"]["tech"])

    # 5) Recommendations (actionable list + narrative summary)
    action_items = recommendation_list(
        missing=scores["missing_flat"],
        skills_section=set(skills_section),
        projects_section=set(projects_section),
        experience_section=set(experience_section),
    )
    summary_text = summarize_strength_gaps(scores)

    # ---------------- UI OUTPUT ----------------
    st.markdown("### 📊 Job Fit Overview")
    st.progress(int(round(overall_pct)))
    st.success(f"Overall Match: **{overall_pct:.1f}%**  —  {verdict}")

    # Category cards
    c1, c2, c3 = st.columns(3)
    c1.metric("Tech Match", f"{scores['tech']['pct']:.1f}%")
    c2.metric("Soft Skills Match", f"{scores['soft']['pct']:.1f}%")
    c3.metric("DevOps/Cloud Match", f"{scores['devops']['pct']:.1f}%")

    # Strengths & gaps (clean narrative)
    st.markdown("### 💡 Summary")
    st.write(summary_text)

    # Missing per-category (compact)
    st.markdown("### ⚠️ Missing (by category)")
    miss_cols = st.columns(3)
    miss_cols[0].write(
        "**Tech:** " + (", ".join(sorted(scores["missing"]["tech"])) or "—")
    )
    miss_cols[1].write(
        "**Soft:** " + (", ".join(sorted(scores["missing"]["soft"])) or "—")
    )
    miss_cols[2].write(
        "**DevOps/Cloud:** " + (", ".join(sorted(scores["missing"]["devops"])) or "—")
    )

    # Actionable list
    st.markdown("### 📝 Actionable Suggestions")
    if action_items:
        for item in action_items:
            st.write("- " + item)
    else:
        st.write("🎉 Looks great! No urgent additions needed for this JD.")

    # Debug / transparency (optional)
    if show_previews:
        st.markdown("---")
        st.markdown("### 🔎 Debug / Previews")
        with st.expander("Extracted Resume Text (first 1000 chars)"):
            st.text(resume_text[:1000])
        with st.expander("Detected Resume Sections"):
            st.json(sections)
        with st.expander("JD NLP Keyphrases + Synonym Expansion"):
            st.write("Keyphrases:", jd_keyphrases)
            st.write("Expanded:", jd_expanded)
        with st.expander("Skill Sets (All)"):
            st.write("Resume skills:", sorted(resume_skills_all))
            st.write("JD skills:", sorted(jd_skills_all))
