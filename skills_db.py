# skills_db.py

# ========= Canonical Skills =========

TECH_SKILLS = {
    # Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "rust", "r", "scala",
    "kotlin", "swift", "php",

    # Web / App
    "html", "css", "bootstrap", "tailwind", "jquery",
    "react", "nextjs", "angular", "vue", "svelte",
    "node", "express", "flask", "django", "spring", ".net", "laravel",

    # Data / ML
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "keras",

    # Databases
    "sql", "mysql", "postgresql", "sqlite", "oracle", "mongodb", "redis", "firebase",
}

SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "problem solving", "critical thinking",
    "creativity", "adaptability", "time management", "collaboration", "decision making",
    "presentation", "public speaking", "analytical thinking", "ownership"
}

DEVOPS_CLOUD_SKILLS = {
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "gitlab", "github", "ci/cd"
}

# ========= Master =========
ALL_SKILLS = TECH_SKILLS | SOFT_SKILLS | DEVOPS_CLOUD_SKILLS
