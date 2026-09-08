from flask import Flask, render_template, request, jsonify
import random
import json
import re
from pathlib import Path

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "questions.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    QUESTION_BANK = json.load(f)

# Add the skill name to every question because questions.json stores
# questions grouped by skill and does not repeat the skill inside each item.
for _skill_name, _questions in QUESTION_BANK.items():
    for _q in _questions:
        _q["skill"] = _skill_name

CAREERS = {
    "Data Analyst": ["SQL", "Python", "Excel", "Statistics", "Power BI"],
    "Python Developer": ["Python", "SQL", "Git", "OOP", "APIs"],
    "Web Developer": ["HTML/CSS", "JavaScript", "Python", "SQL", "APIs"],
    "AI/ML Engineer": ["Python", "Statistics", "Machine Learning", "SQL", "Git"]
}

CAREER_KEYWORDS = {
    "data analyst": ["SQL", "Python", "Excel", "Statistics", "Power BI"],
    "business analyst": ["Excel", "SQL", "Statistics", "Power BI"],
    "data scientist": ["Python", "Statistics", "Machine Learning", "SQL"],
    "machine learning": ["Python", "Machine Learning", "Statistics", "SQL", "Git"],
    "artificial intelligence": ["Python", "Machine Learning", "Statistics", "Git"],
    "ai engineer": ["Python", "Machine Learning", "Statistics", "Git"],
    "software engineer": ["Python", "OOP", "Git", "APIs", "SQL"],
    "software developer": ["Python", "OOP", "Git", "APIs", "SQL"],
    "python developer": ["Python", "SQL", "Git", "OOP", "APIs"],
    "web developer": ["HTML/CSS", "JavaScript", "Python", "SQL", "APIs"],
    "frontend": ["HTML/CSS", "JavaScript", "Git"],
    "backend": ["Python", "APIs", "SQL", "Git", "OOP"],
    "full stack": ["HTML/CSS", "JavaScript", "Python", "SQL", "APIs"],
    "cyber security": ["Python", "SQL", "Git", "APIs"],
    "cybersecurity": ["Python", "SQL", "Git", "APIs"],
}

ROADMAPS = {
    "SQL": ["Learn SELECT, WHERE and ORDER BY", "Practice JOIN, GROUP BY and HAVING", "Build a SQL database project"],
    "Python": ["Learn Python fundamentals", "Practice functions, collections and OOP", "Build a practical Python project"],
    "Excel": ["Master formulas and functions", "Learn PivotTables and charts", "Build an interactive Excel dashboard"],
    "Statistics": ["Learn mean, median, mode and variance", "Practice probability and correlation", "Apply statistics to a real dataset"],
    "Power BI": ["Learn Power Query", "Learn data modeling and DAX", "Build a business dashboard"],
    "Git": ["Learn init, add, commit and push", "Practice branches and merges", "Publish a project on GitHub"],
    "OOP": ["Learn classes, objects and encapsulation", "Practice inheritance and polymorphism", "Build an OOP application"],
    "APIs": ["Understand HTTP, REST and JSON", "Practice GET and POST requests", "Build an API-integrated application"],
    "HTML/CSS": ["Learn semantic HTML", "Master CSS Flexbox, Grid and responsive design", "Build a responsive portfolio"],
    "JavaScript": ["Learn variables, functions and arrays", "Practice DOM, events and async JavaScript", "Build an interactive web app"],
    "Machine Learning": ["Learn supervised and unsupervised learning", "Practice preprocessing and model evaluation", "Build and evaluate an ML project"]
}

ALIASES = {
    "html": "HTML/CSS", "css": "HTML/CSS", "html/css": "HTML/CSS",
    "js": "JavaScript", "javascript": "JavaScript",
    "ml": "Machine Learning", "machine learning": "Machine Learning",
    "powerbi": "Power BI", "power bi": "Power BI",
    "api": "APIs", "apis": "APIs", "oop": "OOP",
}

def normalize_skill(s):
    s = str(s).strip()
    return ALIASES.get(s.lower(), s)

def text_skills(text):
    text = (text or "").lower()
    found = []
    for skill in QUESTION_BANK:
        patterns = [skill.lower()]
        if skill == "HTML/CSS":
            patterns += ["html", "css"]
        if skill == "Power BI":
            patterns += ["powerbi"]
        if skill == "Machine Learning":
            patterns += ["machine learning", "ml"]
        if skill == "JavaScript":
            patterns += ["javascript"]
        if skill == "APIs":
            patterns += ["api", "apis"]
        if any(re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", text) for p in patterns):
            found.append(skill)
    return sorted(set(found))

def parse_skill_list(value):
    if isinstance(value, list):
        items = value
    else:
        items = str(value or "").split(",")
    result = []
    for item in items:
        skill = normalize_skill(item)
        if skill in QUESTION_BANK and skill not in result:
            result.append(skill)
    return result

def infer_skills(career, current_skills="", job_description=""):
    career = str(career or "").strip()
    key = career.lower()
    if career in CAREERS:
        return CAREERS[career][:]
    # Match a known role inside a custom career title.
    for phrase, skills in CAREER_KEYWORDS.items():
        if phrase in key:
            return skills[:]
    # For a completely custom role, infer skills from the student's skills and JD.
    combined = f"{current_skills} {job_description}"
    inferred = text_skills(combined)
    return inferred or list(QUESTION_BANK.keys())

def public_question(q):
    return {
        "id": q["id"],
        "skill": q["skill"],
        "question": q["question"],
        "options": q["options"],
        "difficulty": q.get("difficulty", "medium").title()
    }

def choose_question(skills, history):
    # Adaptive logic: correct -> harder next question; wrong -> easier.
    if not history:
        target_difficulty = "easy"
    else:
        last = history[-1]
        target_difficulty = "hard" if last.get("correct") else "easy"
        if last.get("difficulty") == "easy" and last.get("correct"):
            target_difficulty = "medium"
        elif last.get("difficulty") == "hard" and not last.get("correct"):
            target_difficulty = "medium"

    used = {str(x.get("id")) for x in history}
    # Prefer skills with fewer questions answered.
    counts = {s: 0 for s in skills}
    for x in history:
        if x.get("skill") in counts:
            counts[x["skill"]] += 1
    candidate_skills = sorted(skills, key=lambda s: counts[s])
    for skill in candidate_skills:
        pool = [q for q in QUESTION_BANK.get(skill, []) if str(q["id"]) not in used]
        if not pool:
            continue
        exact = [q for q in pool if q.get("difficulty", "").lower() == target_difficulty]
        if exact:
            return random.choice(exact)
        return random.choice(pool)
    return None

@app.route("/")
def index():
    return render_template("index.html", careers=CAREERS)

@app.post("/api/questions")
def questions():
    data = request.get_json(silent=True) or {}
    career = str(data.get("career", "")).strip()
    if not career:
        return jsonify({"error": "Target career is required"}), 400
    skills = infer_skills(career, data.get("current_skills", ""), data.get("job_description", ""))
    # Initial question for adaptive assessment.
    q = choose_question(skills, [])
    return jsonify({"career": career, "skills": skills, "question": public_question(q) if q else None})

@app.post("/api/next_question")
def next_question():
    data = request.get_json(silent=True) or {}
    career = str(data.get("career", "")).strip()
    skills = data.get("skills") or infer_skills(career, data.get("current_skills", ""), data.get("job_description", ""))
    history = data.get("history", [])
    q = choose_question(skills, history)
    return jsonify({"question": public_question(q) if q else None})

@app.post("/api/check_answer")
def check_answer():
    data = request.get_json(silent=True) or {}
    q = next((q for qs in QUESTION_BANK.values() for q in qs if str(q["id"]) == str(data.get("id"))), None)
    if not q:
        return jsonify({"correct": False}), 404
    return jsonify({"correct": data.get("answer") == q["answer"]})

@app.post("/api/evaluate")
def evaluate():
    data = request.get_json(silent=True) or {}
    career = str(data.get("career", "")).strip()
    answers = data.get("answers", {})
    profile = data.get("profile", {}) or {}
    skills_required = data.get("skills") or infer_skills(
        career, profile.get("current_skills", ""), profile.get("job_description", "")
    )

    all_questions = {
        str(q["id"]): q for skill_questions in QUESTION_BANK.values() for q in skill_questions
    }
    stats = {skill: {"correct": 0, "total": 0} for skill in skills_required}
    for qid, selected in answers.items():
        q = all_questions.get(str(qid))
        if not q or q["skill"] not in stats:
            continue
        stats[q["skill"]]["total"] += 1
        if selected == q["answer"]:
            stats[q["skill"]]["correct"] += 1

    try:
        academic = max(0, min(100, float(profile.get("academic_score", 0) or 0)))
    except (ValueError, TypeError):
        academic = 0

    skills = []
    for skill in skills_required:
        st = stats[skill]
        score = round(st["correct"] / st["total"] * 100) if st["total"] else 0
        adjusted = round(score * 0.8 + academic * 0.2) if academic else score
        level = "Advanced" if adjusted >= 80 else "Intermediate" if adjusted >= 60 else "Beginner" if adjusted >= 40 else "Needs Improvement"
        skills.append({"skill": skill, "score": score, "adjusted_score": adjusted, "level": level,
                       "correct": st["correct"], "total": st["total"]})

    assessment = round(sum(x["score"] for x in skills) / len(skills)) if skills else 0
    overall = round(assessment * 0.8 + academic * 0.2) if academic else assessment

    gaps = sorted(skills, key=lambda x: x["score"])
    recommendations, roadmap = [], []
    for item in gaps[:3]:
        priority = "High" if item["score"] < 60 else "Medium" if item["score"] < 80 else "Low"
        recommendations.append(
            f"{priority} priority: improve {item['skill']} through focused practice and a portfolio project."
            if priority != "Low" else f"Maintain {item['skill']} and attempt an advanced project."
        )
        roadmap.append({"skill": item["skill"], "priority": priority,
                        "steps": ROADMAPS.get(item["skill"], ["Learn fundamentals", "Practice exercises", "Build a project"])})

    resume_text = profile.get("resume_text", "")
    resume_skills = text_skills(resume_text)
    resume_match = round(len(set(skills_required) & set(resume_skills)) / len(skills_required) * 100) if resume_text.strip() and skills_required else None

    jd = profile.get("job_description", "")
    jd_skills = text_skills(jd)
    jd_match = round(len(set(skills_required) & set(jd_skills)) / len(skills_required) * 100) if jd.strip() and skills_required else None
    jd_missing = [s for s in skills_required if s not in jd_skills]

    return jsonify({
        "profile": profile, "career": career, "required_skills": skills_required,
        "assessment_score": assessment, "overall_score": overall,
        "total_correct": sum(x["correct"] for x in stats.values()),
        "total_questions": sum(x["total"] for x in stats.values()),
        "skills": skills, "recommendations": recommendations, "roadmap": roadmap,
        "resume": {"detected_skills": resume_skills, "match": resume_match,
                   "missing_skills": [s for s in skills_required if s not in resume_skills]},
        "job_match": {"detected_skills": jd_skills, "match": jd_match, "missing_skills": jd_missing}
    })

if __name__ == "__main__":
    app.run(debug=True)
