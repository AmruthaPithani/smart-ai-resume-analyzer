from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import sqlite3, io, os
from werkzeug.security import generate_password_hash, check_password_hash
import fitz

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# GPT

app = Flask(__name__)
app.secret_key = "secret123"

print("🔥 App is starting...")

# ---------------- DB ----------------
def init_db():

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        score INTEGER
    )
    """)

    conn.commit()
    conn.close()


def create_demo_user():

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Check if demo user exists
    c.execute(
        "SELECT * FROM users WHERE username=?",
        ("demo",)
    )

    user = c.fetchone()

    # Create demo user only if it doesn't exist
    if not user:

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (
                "demo",
                generate_password_hash("demo123")
            )
        )

    conn.commit()
    conn.close()


# Run database initialization first
init_db()

# Then create demo account
create_demo_user()

# ---------------- PDF SAFE ----------------
def extract_text(file):
    try:
        file.seek(0)
        file_bytes = file.read()

        if not file_bytes:
            return ""

        pdf = fitz.open(stream=file_bytes, filetype="pdf")

        text = ""
        for page in pdf:
            try:
                text += page.get_text()
            except:
                continue

        return text.lower()

    except Exception as e:
        print("PDF ERROR:", e)
        return ""

# ---------------- ATS ----------------
def calculate_ats(text, skills, found):
    skill_score = (len(found)/len(skills))*50 if skills else 0
    length_score = 20 if len(text.split()) > 150 else 10
    keyword_score = 20 if len(found) >= 3 else 10
    structure_score = 10 if ("education" in text or "experience" in text) else 5
    return int(skill_score + length_score + keyword_score + structure_score)

# ---------------- GPT SUGGESTION ----------------
def generate_ai_suggestions(text, role, missing):
    suggestions = []

    # 🔹 Missing Skills
    if missing:
        suggestions.append(f"Add missing skills: {', '.join(missing)}")

    # 🔹 Projects
    if "project" not in text:
        suggestions.append("Include 1–2 strong projects with description and impact")

    # 🔹 Achievements / Numbers
    if "%" not in text and "improved" not in text and "achieved" not in text:
        suggestions.append("Add measurable achievements (e.g., improved performance by 20%)")

    # 🔹 Experience Section
    if "experience" not in text:
        suggestions.append("Add an Experience section or internships")

    # 🔹 Keywords (ATS boost)
    if role:
        suggestions.append(f"Include more {role}-specific keywords to improve ATS score")

    # 🔹 Resume Length
    if len(text.split()) < 120:
        suggestions.append("Expand your resume with more content (skills, projects, certifications)")

    # 🔹 Formatting
    if "@" not in text:
        suggestions.append("Add contact information (email, LinkedIn, GitHub)")

    # 🔹 Default fallback
    if not suggestions:
        suggestions.append("Your resume looks strong. Consider refining formatting and clarity.")

    return " • " + "\n • ".join(suggestions)
# ---------------- Interview Question Generator ----------------
def generate_interview_questions(found):

    questions = []

    for skill in found:

        questions.extend([

            f"Explain a project where you used {skill}.",

            f"What are the advantages of {skill}?",

            f"What challenges did you face while using {skill}?",

            f"How would you optimize performance when working with {skill}?"

        ])

    return questions[:8]
# ---------------- Anomoly Detection ----------------
  
def detect_anomalies(text):

    alerts = []

    if "experience" not in text:
        alerts.append(
            "No experience section detected"
        )

    if "project" not in text:
        alerts.append(
            "No projects section detected"
        )

    if "@" not in text:
        alerts.append(
            "Contact details missing"
        )

    return alerts

# ---------------- JOB DESCRIPTION MATCH ----------------

def calculate_jd_match(text, job_description):

    if not job_description.strip():
        return 0, [], []

    resume_words = set(text.lower().split())
    jd_words = set(job_description.lower().split())

    matched = list(resume_words.intersection(jd_words))
    missing = list(jd_words - resume_words)

    score = int(
        len(matched) /
        max(1, len(jd_words))
        * 100
    )

    return score, matched[:10], missing[:10]


# ---------------- ROLE PREDICTION ----------------

def predict_role(text):

    text = text.lower()

    dev = sum(skill in text for skill in roles["developer"])
    data = sum(skill in text for skill in roles["data"])
    web = sum(skill in text for skill in roles["web"])

    scores = {
        "Software Developer": dev,
        "Data Scientist": data,
        "Web Developer": web
    }

    predicted = max(scores, key=scores.get)

    max_score = max(scores.values())
    if max_score == 0:
        confidence = 0
    else:
        confidence = int(
        scores[predicted] /
        max_score * 100
        )

    return predicted, confidence


# ---------------- SECTION DETECTION ----------------

def detect_sections(text):

    return {

        "Education":
        "education" in text,

        "Skills":
        "skills" in text,

        "Projects":
        "project" in text,

        "Experience":
        "experience" in text,

        "Certifications":
        "certification" in text

    }


# ---------------- GRADE ----------------
def get_grade(score):
    if score >= 80: return "A"
    elif score >= 60: return "B"
    else: return "C"

roles = {
    "developer": ["c","java","python","sql","dsa","oop"],
    "data": ["python","machine learning","statistics","pandas","numpy"],
    "web": ["html","css","javascript","react","node"]
}

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT score FROM history WHERE username=?", (session["user"],))
    scores = [row[0] for row in c.fetchall()]
    conn.close()

    return render_template("index.html", scores=scores)

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (u,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], p):
            session["user"] = u
            return redirect("/")
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    error = None
    if request.method == "POST":
        u = request.form["username"]
        p = generate_password_hash(request.form["password"])

        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("INSERT INTO users(username,password) VALUES(?,?)", (u,p))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            error = "User exists"

    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------- ANALYZE ----------------
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "user" not in session:
            return jsonify({"error": "Login required"}), 401

        file = request.files.get("file")
        role = request.form.get("role", "").lower()
        job_description = request.form.get( "job_description","")

        if not file:
            return jsonify({"error": "Upload file"}), 400

        text = extract_text(file)
        if not text:
            return jsonify({"error": "Invalid PDF"}), 400

        skills = roles.get(role, [])

        found = [s for s in skills if s in text]
        missing = [s for s in skills if s not in text]

        score = int((len(found)/len(skills))*100) if skills else 0
        ats = calculate_ats(text, skills, found)
        grade = get_grade(score)
        suggestion = generate_ai_suggestions(text, role, missing)
        questions = generate_interview_questions(found)
        alerts = detect_anomalies(text)
        jd_score, jd_matched, jd_missing = calculate_jd_match(text,job_description)
        predicted_role, prediction_confidence = predict_role(text)
        sections = detect_sections(text)
        ai_confidence = min(95,score + 10)

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO history (username, score) VALUES (?, ?)",
            (session["user"], score)
        )
        conn.commit()
        conn.close()
        return jsonify({
           "score": score,
           "ats": ats,
           "grade": grade,
           "found": found,
           "missing": missing,
           "suggestion": suggestion,
           "questions": questions,
           "alerts": alerts,
           "jd_score": jd_score,
           "jd_matched": jd_matched,
           "jd_missing": jd_missing,
           "predicted_role": predicted_role,
           "prediction_confidence": prediction_confidence,
           "sections": sections,
           "ai_confidence": ai_confidence
       })

    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({"error": str(e)}), 500

# ---------------- PDF ----------------
@app.route("/download", methods=["POST"])
def download():
    data = request.json

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = [

    Paragraph(
        "Resume Intelligence Report",
        styles["Title"]
    ),

    Paragraph(
        f"Resume Score: {data['score']}%",
        styles["Normal"]
    ),

    Paragraph(
        f"ATS Score: {data['ats']}%",
        styles["Normal"]
    ),

    Paragraph(
        f"Grade: {data['grade']}",
        styles["Normal"]
    ),

    Paragraph(
        f"Matched Skills: {', '.join(data['found'])}",
        styles["Normal"]
    ),

    Paragraph(
        f"Missing Skills: {', '.join(data['missing'])}",
        styles["Normal"]
    ),

    Paragraph(
        "AI Recommendations",
        styles["Heading2"]
    ),

    Paragraph(
        data["suggestion"],
        styles["Normal"]
    )

]

    doc.build(content)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="report.pdf")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
