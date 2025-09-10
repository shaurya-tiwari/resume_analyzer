# utils.py
import os
import requests
import spacy
from dotenv import load_dotenv
from skills_db import ALL_SKILLS, TECH_SKILLS, SOFT_SKILLS, DEVOPS_CLOUD_SKILLS

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# Load .env
load_dotenv()
PPLX_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# -------------------------------
# Cleaning
# -------------------------------
def clean_text(text: str):
    """Lowercase, tokenize, lemmatize (light clean)."""
    doc = nlp(text.lower())
    return [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]

# -------------------------------
# Section Detection
# -------------------------------
def detect_resume_sections(resume_text: str):
    """Naive section splitter based on headings."""
    sections = {}
    current = None
    for line in resume_text.splitlines():
        line_l = line.lower().strip()
        if any(h in line_l for h in ["experience", "work history"]):
            current = "experience"
            sections[current] = []
        elif "project" in line_l:
            current = "projects"
            sections[current] = []
        elif "education" in line_l:
            current = "education"
            sections[current] = []
        elif "skill" in line_l:
            current = "skills"
            sections[current] = []
        elif current:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}

# -------------------------------
# Semantic Skill Matching (Perplexity)
# -------------------------------
def semantic_skill_match(resume_text: str, job_description: str):
    """
    Use Perplexity AI to semantically compare resume vs JD.
    Returns (matched_skills, missing_skills).
    Falls back to simple token overlap if API fails.
    """
    try:
        prompt = f"""
        Compare the following resume and job description.
        Extract SKILLS, TOOLS, FRAMEWORKS only (ignore soft words).
        Return strictly JSON like:
        {{
          "matched": [...],
          "missing": [...]
        }}

        Resume:
        {resume_text[:1000]}

        Job Description:
        {job_description[:800]}
        """

        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PPLX_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sonar-medium-online",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        matched, missing = set(), set()
        # naive parse from JSON-like response
        if "matched" in content.lower():
            import re, json
            try:
                json_block = re.search(r"\{.*\}", content, re.S).group(0)
                parsed = json.loads(json_block)
                matched = set([s.lower() for s in parsed.get("matched", [])])
                missing = set([s.lower() for s in parsed.get("missing", [])])
            except Exception:
                # fallback line parsing
                for line in content.splitlines():
                    if "matched" in line.lower():
                        skills = line.split(":")[-1]
                        matched.update([s.strip().lower() for s in skills.split(",")])
                    if "missing" in line.lower():
                        skills = line.split(":")[-1]
                        missing.update([s.strip().lower() for s in skills.split(",")])

        # final filter with ALL_SKILLS
        matched = {s for s in matched if s in ALL_SKILLS}
        missing = {s for s in missing if s in ALL_SKILLS}

        return matched, missing

    except Exception:
        # Fallback → simple overlap
        resume_tokens = clean_text(resume_text)
        jd_tokens = clean_text(job_description)
        matched = set(resume_tokens) & set(jd_tokens)
        missing = set(jd_tokens) - set(resume_tokens)
        return matched, missing

# -------------------------------
# Scoring
# -------------------------------
def calculate_category_scores(resume_skills, jd_skills, tech_weight=60, soft_weight=20, devops_weight=20):
    """Calculate % match for each skill category and overall score."""

    def pct(a, b):
        return (len(a & b) / len(b) * 100) if b else 0

    tech_match = pct(resume_skills, jd_skills & TECH_SKILLS)
    soft_match = pct(resume_skills, jd_skills & SOFT_SKILLS)
    devops_match = pct(resume_skills, jd_skills & DEVOPS_CLOUD_SKILLS)

    overall = (
        (tech_match * tech_weight)
        + (soft_match * soft_weight)
        + (devops_match * devops_weight)
    ) / (tech_weight + soft_weight + devops_weight)

    return {
        "tech": {"pct": tech_match, "matched": resume_skills & jd_skills & TECH_SKILLS},
        "soft": {"pct": soft_match, "matched": resume_skills & jd_skills & SOFT_SKILLS},
        "devops": {"pct": devops_match, "matched": resume_skills & jd_skills & DEVOPS_CLOUD_SKILLS},
        "overall_score": overall,
        "missing_flat": list(jd_skills - resume_skills),
        "matched_flat": list(resume_skills & jd_skills),
    }

def ats_verdict(overall, missing_tech):
    if overall >= 80:
        return "✅ Strong Fit"
    elif overall >= 60:
        return "⚠️ Moderate Fit"
    else:
        if missing_tech:
            return "❌ Weak Fit (missing: " + ", ".join(missing_tech[:5]) + ")"
        return "❌ Weak Fit"

def recommendation_list(missing, skills_section, projects_section, experience_section):
    recs = []
    for skill in missing:
        if skill in TECH_SKILLS and skill not in skills_section:
            recs.append(f"Add **{skill}** to Skills section.")
        elif skill in TECH_SKILLS and skill not in projects_section:
            recs.append(f"Showcase a project with **{skill}**.")
        elif skill in SOFT_SKILLS and skill not in experience_section:
            recs.append(f"Demonstrate **{skill}** in Experience section.")
    return recs

def summarize_strength_gaps(scores):
    return (
        f"Tech Skills: {scores['tech']['pct']:.1f}% | "
        f"Soft Skills: {scores['soft']['pct']:.1f}% | "
        f"DevOps: {scores['devops']['pct']:.1f}%"
    )

# -------------------------------
# AI (Perplexity) Resume Quality Check
# -------------------------------
def analyze_resume_quality_pplx(resume_text):
    """
    Analyze the uploaded resume (independent of JD).
    Provide ATS-friendliness, missing sections, improvement tips.
    """
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {PPLX_API_KEY}", "Content-Type": "application/json"}

    prompt = f"""
You are an ATS and resume expert. Analyze this resume:

{resume_text[:4000]}

Return a clear report with:
- ATS-friendly? (yes/no with reason)
- Missing key sections (skills, projects, education, etc.)
- General suggestions to improve ATS ranking and clarity , nd try to keep answer short an clear and also say that what points i can skip but  what are  the essesntial improvemnt before upploading  the resume  .
"""

    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

# -------------------------------
# AI Resume Booster (JD-specific)
# -------------------------------
def generate_resume_booster_pplx(missing_skills, job_description, matched_skills=None, overall_score=None):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {PPLX_API_KEY}", "Content-Type": "application/json"}

    matched_text = ", ".join(matched_skills) if matched_skills else "None"
    missing_text = ", ".join(missing_skills) if missing_skills else "None"
    score_text = f"Match Score: {overall_score:.1f}%" if overall_score else "Score unavailable"

    prompt = f"""
You are an ATS and resume expert. Compare my resume against this JD, and tell me am I eligible for this job or not , will my resume short list  or not , and try to give answers in midium short. 

Job Description: {job_description}
Matched Skills: {matched_text}
Missing Skills: {missing_text}
{score_text}

Give practical guidance:
1) Strengths already aligned
3) Should apply now or update resume first?
4) Selection Probability (low/medium/high), make it realistic and accurate 
"""

    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
