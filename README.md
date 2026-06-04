# CampusGPT — AI-Powered University ERP System

CampusGPT is a premium, modern, AI-integrated Campus Management and ERP system designed for universities. Built on top of **Django** and styled with **custom glassmorphic Tailwind CSS**, it features role-specific panels for **Students**, **Faculty**, and **Operational Staff** alongside integrated **AI Agent workflows**.

---

## 🌟 Key Features

### 🎓 1. Student Portal
*   **Daily Timetable & Room Schedules:** Real-time class slot views including room names.
*   **GPA Forecasting Engine:** A credit-weighted GPA predictor mapping current test percentages to a standard 4.0 scale (A=4.0, A-=3.7, B+=3.3, B=3.0, etc.).
*   **Interactive AI Academic Advisor:** A premium, real-time AJAX chat window to discuss grades, timetables, and fee dues.
*   **Notification Center:** Automatic alerts on attendance drops (below 80% warning), new materials, or pending quizzes.
*   **Course Materials & Fees:** Instantly review uploaded slides, external links, and paid/partial/due fee structures.

### 👨‍🏫 2. Faculty Portal
*   **Section Manager:** Take and save daily attendance with simple selection switches.
*   **AI Quiz Generator:** Automatically construct multiple-choice or short-answer quizzes by pasting lecture notes.
*   **Course Resources:** Upload slides, PDFs, or external links for specific sections.
*   **At-Risk Students Panel:** Instantly flags weak students whose attendance falls below 80% or grade average below 60%.

### ⚙️ 3. Operational Staff Portal
*   **Duty Scheduling:** Monitor assigned campus duties, start/end hours, and location assignments.
*   **Leave Management:** Submit leave requests digitally and track approval status (Approved, Pending, Rejected).
*   **Payroll slips:** Review monthly gross vs. paid salaries.

---

## 💻 Tech Stack

*   **Backend:** Python 3.14+ / Django 5.2+ / Django REST Framework
*   **Frontend:** Django Templates / Tailwind CSS / Vanilla AJAX JS / Custom Premium Styles (Glassmorphism & animations defined in `static/css/modern.css`)
*   **AI Layer:** OpenAI Chat API (with context-aware database-driven fallback system when API key is missing)
*   **Database:** SQLite3 / SQLite Relational Model

---

## 🚀 Setup & Execution

### 1. Environment Setup
Install dependencies and configure your environment:
```bash
# Install dependencies using uv or pip
pip install -r pyproject.toml
```

### 2. Configure OpenAI Key (Optional)
If you wish to use live LLM calls for the Academic Advisor and Quiz Generator, set the environment variable:
```bash
# On Windows
$env:OPENAI_API_KEY="your-api-key-here"
```
*Note: If no API key is set, the system automatically falls back to an intelligent, database-aware rules simulator.*

### 3. Run Migrations & Seed Data
Initialize the database and populate it with rich demo records:
```bash
# Apply migrations
python manage.py migrate

# Seed database with student, faculty, and staff demo users
python manage.py seed_demo
```

**Default Demo Credentials:**
*   **Student:** Username: `su92-bsdsm-001` / Password: `StudentPass123!`
*   **Faculty:** Username: `ahmed` / Password: `FacultyPass123!`
*   **Operational Staff:** Username: `lib_aslam` / Password: `StaffPass123!`
*   **Admin Panel:** Access at `http://127.0.0.1:8000/admin/`

### 4. Run Server
Start the development server:
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your web browser.

---

## 🧪 Unit Testing

Run the test suite containing 29 validation tests for authentication, database constraints, models, and dashboards:
```bash
python manage.py test
```
