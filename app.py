import streamlit as st
import pdfplumber
import docx
import re
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
    return "\n".join([para.text for para in doc.paragraphs])

# Better cleaner
def clean_text(text):
    return re.findall(r"[a-zA-Z+#]+", text.lower())

# -------------------------------
# Streamlit App
# -------------------------------
st.title("📄 AI Resume Analyzer (Improved Edition)")

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
    elif resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = extract_text_from_docx(resume_file)

if st.button("🔍 Analyze"):
    if resume_text and job_description:
        resume_tokens = clean_text(resume_text)
        jd_tokens = clean_text(job_description)

        resume_skills = extract_skills(resume_tokens, SKILLS_DB)
        jd_skills = extract_skills(jd_tokens, SKILLS_DB)

        job_fit, status, matched, missing = calculate_weighted_score(resume_skills, jd_skills)

        # Results Section
        st.subheader("📊 Job Fit Score:")
        st.progress(int(job_fit))
        st.success(f"Your Resume matches {job_fit}% with the Job Description")
        st.info(status)

        # Recommendations
        st.subheader("💡 Personalized Recommendation:")
        if matched:
            st.write(f"✅ Strengths: {', '.join(matched)}")
        if missing:
            st.write(f"⚠️ Missing: {', '.join(missing)}")
            st.write("👉 Add relevant projects, certifications, or internships for these skills.")
        if not matched and not missing:
            st.write("⚠️ No major relevant skills detected. Tailor resume with job-related keywords.")
