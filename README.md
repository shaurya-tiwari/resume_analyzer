AI Resume Analyzer — JD-Based Resume Evaluation App

<!-- Replace with your screenshot -->
<h2>Demo Video</h2>
<p>Watch a demo of the Resume Analyzer in action:</p>
<a href="https://www.dropbox.com/scl/fi/5bnimrjb4r7e2ktyezmf2/DemoVideo.mp4?rlkey=czxj1nfxv7kyn3e99rqskr4xu&st=mhosesjs&dl=0" target="_blank">
    View on Dropbox
</a>

A web application that analyzes resumes against job descriptions to evaluate skill match, ATS compatibility, and overall job fit using AI/ML techniques. Built as a hands-on project to apply Generative AI and NLP concepts learned during AWS AI/ML training.

🚀 Features

Upload PDF or DOCX resumes for analysis

Detects resume sections: Skills, Projects, Experience, Education

Performs semantic skill matching using Perplexity AI API

Calculates category scores: Tech, Soft, DevOps, and overall fit

Generates ATS verdict and actionable recommendations

Provides JD-specific AI resume booster to improve job match

General resume quality check for ATS optimization

🛠 Tech Stack

Backend & UI: Python, Streamlit

Resume Parsing: pdfplumber, python-docx

NLP & AI: spaCy, Perplexity AI API

Environment Variables: python-dotenv

Other: Data cleaning, tokenization, section detection

📂 Project Structure
resume-analyzer/
├── app.py                  # Streamlit app frontend + main logic
├── utils.py                # Helper functions: text cleaning, scoring, AI calls
├── skills_db.py            # Skills database (tech, soft, devops)
├── requirements.txt        # Python dependencies
└── README.md               # This file

💻 Installation & Setup

Clone the repository:

git clone https://github.com/shaurya-tiwari/resume-analyzer.git
cd resume-analyzer


Install dependencies:

pip install -r requirements.txt


Add your Perplexity API key in a .env file:

PERPLEXITY_API_KEY=your_api_key_here


Run the app:

streamlit run app.py


Open the URL shown in your terminal (http://localhost:8501)

🎯 Usage

Upload a PDF or DOCX resume.

Paste the Job Description into the text area.

Click Analyze to get:

Skill match overview

ATS verdict

JD-specific resume booster

Resume quality insights

⚡ Highlights

Demonstrates practical application of AI/ML to real-world HR and recruitment problems

Integrates semantic AI for smarter skill matching

Provides actionable feedback to improve job-fit and ATS ranking

📌 Notes

Tested with Python 3.10+

Requires internet access for Perplexity AI API calls

Streamlit UI provides easy-to-read insights for any resume
