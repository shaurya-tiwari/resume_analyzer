import streamlit as st
import pdfplumber
import docx
from utils import extract_skills, calculate_weighted_score
from skills_db import SKILLS_DB


# -------------------------------
# Functions to extract text
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
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


# Simple text cleaner
def clean_text(text):
    tokens = text.lower().split()
    return [t.strip(".,:;!?()[]{}") for t in tokens if t.isalpha() or t.isalnum()]


# -------------------------------
# Streamlit App
# -------------------------------
st.title("📄 AI Resume Analyzer (Practical Edition)")

col1, col2 = st.columns(2)

with col1:
    st.header("Upload Resume")
    resume_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])

with col2:
    st.header("Paste Job Description")
    job_description = st.text_area("Enter Job Description here...")

resume_text = ""
if resume_file is not None:
    if resume_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(resume_file)
    elif (
        resume_file.type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        resume_text = extract_text_from_docx(resume_file)

if st.button("🔍 Analyze"):
    if resume_text and job_description:
        resume_tokens = clean_text(resume_text)
        jd_tokens = clean_text(job_description)

        resume_skills = extract_skills(resume_tokens, SKILLS_DB)
        jd_skills = extract_skills(jd_tokens, SKILLS_DB)

        # Weighted Scoring
        job_fit, status, matched, missing = calculate_weighted_score(
            resume_skills, jd_skills
        )

        # Results Section
        st.subheader("📊 Job Fit Score:")
        st.progress(int(job_fit))
        st.success(f"Your Resume matches {job_fit}% with the Job Description")
        st.info(status)

        # Smart Recommendation Paragraph
        recommendation = ""

        if matched:
            recommendation += (
                f"✅ Your resume already highlights strengths in {', '.join(matched)}. "
            )

        if missing:
            recommendation += f"⚠️ However, you are missing important skills like {', '.join(missing)}. "
            recommendation += "Consider adding projects, certifications, or internships that demonstrate these skills. "

        if not matched and not missing:
            recommendation = "⚠️ No major relevant skills detected in your resume. Try tailoring it with more job-related keywords."

        if not missing:
            recommendation += " 🎉 Great job! Your resume already covers the critical skills required for this role."

        st.subheader("💡 Personalized Recommendation:")
        st.write(recommendation)
