# skills_db.py

# ====== Canonical Skills (lowercase) ======
TECH_SKILLS = {
    # Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "rust", "r", "scala",
    "kotlin", "swift", "php", "matlab",

    # Web & App
    "html", "css", "bootstrap", "tailwind", "jquery",
    "react", "nextjs", "angular", "vue", "svelte",
    "node", "express", "flask", "django", "spring", ".net", "laravel",

    # Data / ML
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "keras",

    # Databases
    "sql", "mysql", "postgresql", "sqlite", "oracle", "mongodb", "redis", "cassandra", "firebase",
}

SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "problem solving", "critical thinking",
    "creativity", "adaptability", "time management", "collaboration", "decision making",
    "presentation", "public speaking", "analytical thinking", "ownership"
}

DEVOPS_CLOUD_SKILLS = {
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "gitlab", "github", "ci/cd",
}

# A compact master set
ALL_SKILLS = TECH_SKILLS | SOFT_SKILLS | DEVOPS_CLOUD_SKILLS

# ====== Synonyms / Phrases → Canonical Skills ======
# Left side: phrases that may appear in JD; right side: canonical skill(s) we map to.
SYNONYMS = {
    # DB & Data
    "relational database": ["sql", "mysql", "postgresql"],
    "rdbms": ["sql", "mysql", "postgresql"],
    "data visualization": ["matplotlib", "seaborn", "plotly"],

    # DevOps/Cloud
    "containerization": ["docker", "kubernetes"],
    "orchestration": ["kubernetes"],
    "cloud platform": ["aws", "azure", "gcp"],
    "cicd": ["ci/cd", "jenkins", "gitlab"],
    "continuous integration": ["ci/cd", "jenkins", "gitlab"],
    "continuous delivery": ["ci/cd", "jenkins", "gitlab"],

    # Frontend
    "frontend": ["react", "angular", "vue"],
    "spa": ["react", "angular", "vue"],
    "component based": ["react"],

    # Backend / APIs
    "rest api": ["flask", "django", "express", "node"],
    "microservices": ["docker", "kubernetes"],

    # ML/NLP
    "natural language processing": ["nlp"],
    "llm": ["nlp"],
    "neural network": ["deep learning"],

    # Misc
    "version control": ["github", "gitlab"],
}

# Optional: map some frequent misspellings to canonical forms
MISSPELLINGS = {
    "javasript": "javascript",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "postgress": "postgresql",
}
