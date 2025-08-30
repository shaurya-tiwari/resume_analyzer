import re
from collections import defaultdict
from skills_db import (
    TECH_SKILLS,
    SOFT_SKILLS,
    DEVOPS_CLOUD_SKILLS,
    ALL_SKILLS,
    SYNONYMS,
    MISSPELLINGS,
)


# Optional imports (graceful fallbacks)
try:
    import spacy

    _NLP = spacy.load("en_core_web_sm")
except Exception:
    _NLP = None

try:
    # fallback TF-IDF for keyphrase extraction
    from sklearn.feature_extraction.text import TfidfVectorizer
except Exception:
    TfidfVectorizer = None


# -------------------------------
# Basic cleaning
# -------------------------------
def clean_text(text: str):
    """
    Regex tokenizer that lowercases and keeps only meaningful tokens (words & tech tokens like c#, c++).
    """
    # capture words and tech-y tokens (letters, +, #)
    return re.findall(r"[a-zA-Z][a-zA-Z+#]+", text.lower())


# -------------------------------
# Resume section detection
# -------------------------------
_SECTION_PATTERNS = [
    ("skills", r"\bskills?\b|technical skills|core skills"),
    ("projects", r"\bprojects?\b|personal projects|academic projects"),
    (
        "experience",
        r"\bexperience\b|work experience|professional experience|internship",
    ),
    ("education", r"\beducation\b|academics|qualification"),
]


def detect_resume_sections(text: str):
    """
    Very light-weight section detector using common headings.
    Returns a dict with keys: skills, projects, experience, education.
    """
    result = {"skills": "", "projects": "", "experience": "", "education": ""}
    lines = text.splitlines()
    current_key = None

    # precompile
    compiled = [(k, re.compile(pat, re.I)) for (k, pat) in _SECTION_PATTERNS]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        matched_section = None
        for key, rgx in compiled:
            if rgx.search(stripped):
                matched_section = key
                break
        if matched_section:
            current_key = matched_section
            continue
        if current_key:
            result[current_key] += stripped + " "

    # If nothing detected, put full text into experience as a safe default
    if not any(result.values()):
        result["experience"] = text
    return {k: v.strip() for k, v in result.items()}


# -------------------------------
# NLP Keyword Extraction (JD)
# -------------------------------
def _spacy_keyphrases(text: str, top_k: int = 12):
    """
    Use spaCy noun-chunks & entities as keyphrases; return unique lowercased phrases.
    """
    if not _NLP:
        return []
    doc = _NLP(text)
    phrases = set()

    for nc in doc.noun_chunks:
        token_text = nc.text.strip().lower()
        if 2 <= len(token_text) <= 60:
            phrases.add(token_text)
    for ent in doc.ents:
        token_text = ent.text.strip().lower()
        if 2 <= len(token_text) <= 60:
            phrases.add(token_text)

    # Sort by length desc (rough proxy for specificity), take top_k
    sorted_phrases = sorted(list(phrases), key=lambda s: (-len(s), s))
    return sorted_phrases[:top_k]


def _tfidf_keyphrases(text: str, top_k: int = 12):
    """
    TF-IDF fallback: treat each sentence as a 'doc' and pick top terms.
    """
    if not TfidfVectorizer:
        return []
    sents = [s.strip() for s in re.split(r"[.\n]", text) if s.strip()]
    if not sents:
        sents = [text]
    vec = TfidfVectorizer(ngram_range=(1, 3), stop_words="english")
    try:
        X = vec.fit_transform(sents)
    except Exception:
        return []
    # average tfidf score across sentences for each term
    scores = X.mean(axis=0).A1
    terms = vec.get_feature_names_out()
    ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    return [t for t, _ in ranked[:top_k]]


def nlp_extract_keywords(text: str, top_k: int = 12):
    """
    Try spaCy noun-chunks/entities; if unavailable, fallback to TF-IDF.
    """
    phrases = _spacy_keyphrases(text, top_k=top_k)
    if not phrases:
        phrases = _tfidf_keyphrases(text, top_k=top_k)
    # If both empty, fallback to simple tokens
    if not phrases:
        phrases = list(dict.fromkeys(clean_text(text)))[:top_k]
    return phrases


# -------------------------------
# Synonym expansion
# -------------------------------
def expand_with_synonyms(phrases):
    """
    Expand JD keyphrases with mapped synonyms → canonical skills.
    e.g., 'containerization' → ['docker', 'kubernetes']
    """
    expanded = set(phrases)
    for p in phrases:
        p_norm = p.lower().strip()
        if p_norm in SYNONYMS:
            for mapped in SYNONYMS[p_norm]:
                expanded.add(mapped)
    return list(expanded)


# -------------------------------
# Skill extraction (exact + short-skill context)
# -------------------------------
def extract_skills_exact(tokens, skills_db):
    """
    Exact, case-insensitive word/phrase match against skills_db.
    Short skills (c, r, go) require nearby 'programming' or 'language'.
    """
    found = set()
    text = " ".join(tokens)

    for skill in skills_db:
        s = skill.lower()
        pat = r"\b" + re.escape(s) + r"\b"

        # short skills special case
        if s in {"c", "r", "go"}:
            if re.search(pat, text):
                ctx1 = r"\b" + re.escape(s) + r"\b\s+(language|programming)"
                ctx2 = r"(language|programming)\s+\b" + re.escape(s) + r"\b"
                if re.search(ctx1, text) or re.search(ctx2, text):
                    found.add(s)
        else:
            if re.search(pat, text):
                found.add(s)
    return list(found)


# -------------------------------
# Category scoring
# -------------------------------
def _category_split(skill_set):
    return {
        "tech": set(skill_set) & set(TECH_SKILLS),
        "soft": set(skill_set) & set(SOFT_SKILLS),
        "devops": set(skill_set) & set(DEVOPS_CLOUD_SKILLS),
    }


def calculate_category_scores(
    resume_skills, jd_skills, tech_weight=60, soft_weight=40, devops_weight=20
):
    """
    Compute per-category matches and overall weighted score.
    Only JD skills in a category contribute to that category's denominator.
    """
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    cat_resume = _category_split(resume_set)
    cat_jd = _category_split(jd_set)

    def pct(matched, total):
        return (len(matched) / max(1, len(total))) * 100.0

    # Per-category matches/pcts
    tech_matched = cat_resume["tech"] & cat_jd["tech"]
    soft_matched = cat_resume["soft"] & cat_jd["soft"]
    devops_matched = cat_resume["devops"] & cat_jd["devops"]

    tech_pct = pct(tech_matched, cat_jd["tech"])
    soft_pct = pct(soft_matched, cat_jd["soft"])
    devops_pct = pct(devops_matched, cat_jd["devops"])

    # Missing per category
    tech_missing = cat_jd["tech"] - cat_resume["tech"]
    soft_missing = cat_jd["soft"] - cat_resume["soft"]
    devops_missing = cat_jd["devops"] - cat_resume["devops"]

    # If a category doesn’t appear in the JD, we don’t include its weight
    active_weights = []
    weighted_sum = 0.0

    if len(cat_jd["tech"]) > 0:
        active_weights.append(tech_weight)
        weighted_sum += tech_pct * tech_weight
    if len(cat_jd["soft"]) > 0:
        active_weights.append(soft_weight)
        weighted_sum += soft_pct * soft_weight
    if len(cat_jd["devops"]) > 0:
        active_weights.append(devops_weight)
        weighted_sum += devops_pct * devops_weight

    denom = sum(active_weights) if active_weights else 1
    overall_score = round(weighted_sum / denom, 2)

    return {
        "tech": {
            "matched": sorted(tech_matched),
            "missing": sorted(tech_missing),
            "pct": tech_pct,
        },
        "soft": {
            "matched": sorted(soft_matched),
            "missing": sorted(soft_missing),
            "pct": soft_pct,
        },
        "devops": {
            "matched": sorted(devops_matched),
            "missing": sorted(devops_missing),
            "pct": devops_pct,
        },
        "missing": {
            "tech": sorted(tech_missing),
            "soft": sorted(soft_missing),
            "devops": sorted(devops_missing),
        },
        "missing_flat": sorted(tech_missing | soft_missing | devops_missing),
        "overall_score": overall_score,
    }


# -------------------------------
# Verdict + Recommendations
# -------------------------------
def ats_verdict(overall_pct, tech_missing_list):
    """
    Simple ATS-style verdict with emphasis on tech gaps.
    """
    if overall_pct >= 80 and len(tech_missing_list) == 0:
        return "✅ Strong Match — Likely to pass ATS"
    if overall_pct >= 50:
        return "⚠️ Moderate Match — Can pass with improvements"
    return "❌ Weak Match — Unlikely to pass; add core tech skills"


def recommendation_list(missing, skills_section, projects_section, experience_section):
    """
    Generate actionable suggestions for missing skills and weak sections.
    Adds cross-section tips: if a skill is in resume overall but not in Projects/Experience, nudge to show impact.
    """
    suggestions = []
    missing = set(missing)

    # Missing skills → concrete actions
    for s in sorted(missing):
        if s in {"sql", "mysql", "postgresql"}:
            suggestions.append(
                f"📊 Add a small project showcasing SQL queries (joins, indexes) and mention DB used."
            )
        elif s in {"docker", "kubernetes"}:
            suggestions.append(
                f"🐳 Add a deployment section: containerize an app with {s}, include commands & repo link."
            )
        elif s in {"react", "node", "javascript", "typescript"}:
            suggestions.append(
                f"💻 Build a web project using {s} and link live demo + GitHub."
            )
        elif s in {"python", "java", "c", "c++"}:
            suggestions.append(
                f"🔧 Add coding/project bullets for {s} with metrics (speedup %, users, accuracy)."
            )
        elif s in {"aws", "azure", "gcp"}:
            suggestions.append(
                f"☁️ Mention a cloud-deployed project and basic certification for {s.upper()}."
            )
        elif s in {"communication", "teamwork", "leadership"}:
            suggestions.append(
                f"🧑‍🤝‍🧑 Add evidence under projects/experience to prove {s} (team size, role)."
            )
        else:
            suggestions.append(
                f"📝 Include {s} via a project, internship, or certification, with measurable outcomes."
            )

    # Cross-section nudges — show skills where they matter
    # If skill appears in Skills-section but not in Projects/Experience: push to demonstrate
    showable = (skills_section - projects_section) | (
        skills_section - experience_section
    )
    for s in sorted(showable):
        suggestions.append(
            f"🔎 You list **{s}** in Skills — add it under a Project/Experience bullet with evidence."
        )

    return suggestions


def summarize_strength_gaps(scores):
    """
    Build a friendly narrative summary based on category matches/gaps.
    """
    strengths = []
    if scores["tech"]["matched"]:
        strengths.append(f"Tech: {', '.join(scores['tech']['matched'])}")
    if scores["soft"]["matched"]:
        strengths.append(f"Soft: {', '.join(scores['soft']['matched'])}")
    if scores["devops"]["matched"]:
        strengths.append(f"DevOps/Cloud: {', '.join(scores['devops']['matched'])}")

    gaps = []
    if scores["missing"]["tech"]:
        gaps.append(f"Tech: {', '.join(scores['missing']['tech'])}")
    if scores["missing"]["soft"]:
        gaps.append(f"Soft: {', '.join(scores['missing']['soft'])}")
    if scores["missing"]["devops"]:
        gaps.append(f"DevOps/Cloud: {', '.join(scores['missing']['devops'])}")

    text = ""
    if strengths:
        text += "✅ Strengths — " + " | ".join(strengths) + ". "
    if gaps:
        text += "⚠️ Gaps — " + " | ".join(gaps) + ". "
    if not strengths and not gaps:
        text = "No major skills detected. Tailor your resume with job-related keywords."
    return text
