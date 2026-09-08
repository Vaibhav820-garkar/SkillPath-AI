# SkillPath AI — Complete Competition Prototype

## End-to-end flow

Student Profile
→ Current Skills
→ Academic Performance
→ Target Career
→ Random MCQ Assessment
→ Skill Gap Detection
→ AI Recommendation
→ Personalized Roadmap

## Features

- Student profile form
- Current skills input
- Academic performance input
- Target career selection
- Random questions from a skill-specific question bank
- Skill-wise assessment scoring
- Career readiness score
- Skill gap detection
- Priority-based recommendations
- Personalized roadmap for the weakest skills
- Responsive dashboard
- Offline prototype; no paid API required

## Libraries

- Flask 3.1.2
- Python standard library: json, random, pathlib

Frontend:
- HTML5
- CSS3
- JavaScript

No database is required for this prototype.

## Run on Windows

1. Extract the ZIP.
2. Open PowerShell inside the project folder.
3. Run:

py -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

python app.py

4. Open:
http://127.0.0.1:5000

If PowerShell blocks activation:

venv\Scripts\activate.bat

Then:

pip install -r requirements.txt
python app.py

## How to explain the AI to judges

"The system combines a skill-specific question bank, randomized assessment, skill-wise scoring, academic performance as a secondary signal, gap prioritization, and personalized recommendations. The current prototype uses rule-based intelligent scoring. In the next version, NLP can extract skills from resumes and job descriptions, and a machine-learning model can predict career readiness."

## Important limitation

MCQ performance is an assessment signal, not a complete proof of real-world skill. A production system should combine MCQs with projects, practical tasks, resume evidence and certifications.

## Project structure

AI_Skill_Gap_Analyzer/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── questions.json
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js


## New competition features
- **Custom Target Career:** the student can type any target career; the career is not limited to the four examples.
- **Adaptive MCQ Assessment:** after each answer, the next question difficulty changes based on performance.
- **Resume Analyzer:** paste resume text to extract supported technical skills and calculate career skill match.
- **Job Description Matcher:** paste a job description to identify supported skills and compare requirements.
- **Personalized Skill Gap + Roadmap:** weakest skills receive priority recommendations and learning steps.

### Important
For a completely new career name, enter current skills and/or paste a job description containing skills from the supported question bank (SQL, Python, Excel, Statistics, Power BI, Git, OOP, APIs, HTML/CSS, JavaScript, Machine Learning). This prototype uses a rule-based skill matcher; it does not claim that an MCQ alone proves real-world expertise.
