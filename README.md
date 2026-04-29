# 🧠 Smart AI Resume Analyzer

🚀 **Analyze. Score. Improve. Your Resume.**

Smart AI Resume Analyzer is a full-stack web application that evaluates resumes using ATS (Applicant Tracking System) logic. It analyzes uploaded PDF resumes, matches skills based on job roles, calculates scores, and provides intelligent suggestions for improvement.

---

## 🔥 Features

* 📄 Upload Resume (PDF)
* 🧠 ATS Score Calculation
* 📊 Skill Matching Based on Job Role
* 🏆 Resume Grade (A / B / C)
* 📈 Score History Tracking
* 🧾 Resume Preview
* 📄 Download Report as PDF
* 🔐 User Authentication (Login/Register)
* 🧠 Smart AI Suggestions (Offline – No API required)
* ⚡ Fast and Lightweight (No external AI dependency)

---

## 🧠 How It Works

1. Upload your resume (PDF format)
2. Select a job role (Developer / Data Scientist / Web Developer)
3. System extracts text using PyMuPDF
4. Matches resume skills with predefined role-based skills
5. Calculates:

   * Resume Score
   * ATS Score
   * Resume Grade
6. Generates intelligent suggestions
7. Stores history for performance tracking
8. Allows downloading a PDF report

---

## 📊 Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Flask (Python)
* **Database:** SQLite
* **Libraries Used:**

  * PyMuPDF (PDF parsing)
  * ReportLab (PDF generation)
  * Chart.js (data visualization)

---

## 📁 Project Structure

```
Smart-AI-Resume-Analyzer/
│── app.py
│── users.db
│── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── register.html
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
```

---

## ⚙️ Installation (Run Locally)

```bash
git clone https://github.com/yourusername/smart-ai-resume-analyzer.git
cd smart-ai-resume-analyzer
pip install -r requirements.txt
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

## 🌐 Deployment

This project can be deployed using Render.

### Steps:

1. Push code to GitHub
2. Go to Render → New Web Service
3. Connect your repository
4. Configure:

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn app:app
```

---

## 🎯 Use Cases

* Resume evaluation for students
* Placement preparation
* Skill gap analysis
* ATS optimization
* Career guidance tools

---

## 🧪 Example Output

* ✅ Found Skills: Python, SQL
* ❌ Missing Skills: DSA, OOP
* 📊 Score: 66%
* 🧠 ATS Score: 72%
* 🏆 Grade: B

---

## 🔮 Future Enhancements

* 🧠 Real AI integration (OpenAI / Gemini)
* 📊 Skill radar charts
* 👥 Resume comparison system
* 🌐 Cloud database (MongoDB / Firebase)
* 📱 Mobile responsive UI enhancements

---

## 👩‍💻 Author

**Amrutha Pithani**

---
