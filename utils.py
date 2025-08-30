import re


def extract_skills(tokens, skills_db):
    """
    Extract skills from tokens using exact match + context rules.
    """
    found = set()
    text = " ".join(tokens)

    for skill in skills_db:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        # Special case: short skills like "c", "r"
        if skill.lower() in ["c", "r", "go"]:
            if re.search(pattern, text):
                # Check context: must have "language" or "programming"
                context_pattern = r"(language|programming)\s+" + re.escape(
                    skill.lower()
                )
                context_pattern2 = (
                    re.escape(skill.lower()) + r"\s+(language|programming)"
                )
                if re.search(context_pattern, text) or re.search(
                    context_pattern2, text
                ):
                    found.add(skill.lower())
        else:
            if re.search(pattern, text):
                found.add(skill.lower())

    return list(found)


def calculate_weighted_score(resume_skills, jd_skills):
    """
    Weighted scoring:
    - Tech Skills: 70%
    - Soft Skills: 20%
    - Bonus Skills: 10%
    """
    matched = set(resume_skills) & set(jd_skills)
    missing = set(jd_skills) - set(resume_skills)

    # Categories
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
    total_score = 0
    if jd_skills:
        tech_score = (len(matched & tech_keywords) / len(jd_skills)) * 70
        soft_score = (len(matched & soft_keywords) / len(jd_skills)) * 20
        bonus_score = (len(matched & bonus_keywords) / len(jd_skills)) * 10
        total_score = round(tech_score + soft_score + bonus_score, 2)

    # Status
    if total_score >= 80:
        status = "✅ Strong Match - Highly Eligible"
    elif total_score >= 50:
        status = "⚠️ Moderate Match - Can Apply but Improve Resume"
    else:
        status = "❌ Weak Match - Not Eligible Yet"

    return total_score, status, matched, missing
