import re


# -------------------------------
# Extract skills with exact match
# -------------------------------
def extract_skills(tokens, skills_db):
    """Check tokens against SKILLS_DB with exact word match & special rules for short skills"""
    found = set()
    text = " ".join(tokens)

    for skill in skills_db:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        # --- Special Case Handling ---
        if skill.lower() in ["c", "r", "go"]:
            if re.search(pattern, text):
                # Must have "language" or "programming" context
                context_pattern = (
                    r"\b" + re.escape(skill.lower()) + r"\b\s+(language|programming)"
                )
                context_pattern2 = (
                    r"(language|programming)\s+\b" + re.escape(skill.lower()) + r"\b"
                )
                if re.search(context_pattern, text) or re.search(
                    context_pattern2, text
                ):
                    found.add(skill.lower())
        else:
            if re.search(pattern, text):
                found.add(skill.lower())

    return list(found)


# -------------------------------
# Weighted Job Fit Scoring
# -------------------------------
def calculate_weighted_score(resume_skills, jd_skills):
    """
    Weighted scoring system:
    - Tech Skills: 70%
    - Soft Skills: 20%
    - Bonus Skills (DevOps/Cloud/DB): 10%
    """

    matched = set(resume_skills) & set(jd_skills)
    missing = set(jd_skills) - set(resume_skills)

    # Define categories
    tech_keywords = {
        "python",
        "java",
        "c",
        "c++",
        "c#",
        "javascript",
        "typescript",
        "react",
        "node",
        "django",
        "flask",
        "spring",
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
        "seaborn",
        "plotly",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "keras",
    }

    soft_keywords = {
        "communication",
        "leadership",
        "teamwork",
        "problem solving",
        "critical thinking",
        "creativity",
        "adaptability",
        "time management",
        "collaboration",
        "decision making",
    }

    bonus_keywords = {
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "jenkins",
        "terraform",
    }

    # Scores
    tech_matched = matched & tech_keywords
    soft_matched = matched & soft_keywords
    bonus_matched = matched & bonus_keywords

    total_score = 0
    if jd_skills:
        tech_score = (len(tech_matched) / len(jd_skills)) * 70
        soft_score = (len(soft_matched) / len(jd_skills)) * 20
        bonus_score = (len(bonus_matched) / len(jd_skills)) * 10
        total_score = round(tech_score + soft_score + bonus_score, 2)

    # Eligibility classification
    if total_score >= 80:
        status = "✅ Strong Match - Highly Eligible"
    elif total_score >= 50:
        status = "⚠️ Moderate Match - Can Apply but Improve Resume"
    else:
        status = "❌ Weak Match - Not Eligible Yet"

    return total_score, status, matched, missing
