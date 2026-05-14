from decimal import Decimal

from django.conf import settings


def attendance_summary(enrollment):
    records = enrollment.attendance_records.all()
    total = records.count()
    present = records.filter(status__in=["present", "late", "excused"]).count()
    percentage = round((present / total) * 100, 2) if total else 0
    if percentage >= 80:
        risk = "safe"
    elif percentage >= 70:
        risk = "watch"
    else:
        risk = "risk"
    return {"total": total, "present": present, "percentage": percentage, "risk": risk}


def student_attendance_overview(enrollments):
    rows = []
    for enrollment in enrollments:
        summary = attendance_summary(enrollment)
        rows.append({"enrollment": enrollment, **summary})
    return rows


def predict_sgpa(enrollments):
    percentages = []
    for enrollment in enrollments:
        for grade in enrollment.grade_records.all():
            percentages.append(grade.percentage)
    if not percentages:
        return {"sgpa": 0, "cgpa": 0, "message": "Add grades to enable prediction."}

    avg = sum(percentages) / len(percentages)
    sgpa = round(min(4, max(0, avg / 25)), 2)
    return {
        "sgpa": sgpa,
        "cgpa": sgpa,
        "message": "Prediction uses current marks as a simple MVP estimate.",
    }


def weak_student_rows(section):
    rows = []
    for enrollment in section.enrollments.filter(status="enrolled"):
        attendance = attendance_summary(enrollment)
        grade_values = [grade.percentage for grade in enrollment.grade_records.all()]
        avg_grade = round(sum(grade_values) / len(grade_values), 2) if grade_values else None
        if attendance["risk"] != "safe" or (avg_grade is not None and avg_grade < 60):
            rows.append(
                {
                    "student": enrollment.student,
                    "attendance": attendance,
                    "average_grade": avg_grade,
                    "suggestion": "Schedule a check-in and share focused practice material.",
                }
            )
    return rows


def answer_academic_question(user_label, question, context=None):
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if api_key:
        return (
            "AI provider is configured, but live model calls are intentionally kept "
            "behind this adapter for the MVP. Connect the provider here for production."
        )

    topic = (question or "").lower()
    context = context or {}
    if "attendance" in topic:
        return "Your attendance risk is calculated from marked classes. Keep each course at 80% or above."
    if "fee" in topic or "dues" in topic:
        return "Fee records are shown on your dashboard with paid amount, balance, status, and due date."
    if "quiz" in topic or "assignment" in topic:
        return "Upcoming quizzes and assignments appear in your dashboard deadline list."
    if "gpa" in topic or "cgpa" in topic or "sgpa" in topic:
        return "The MVP predicts SGPA/CGPA from your current recorded marks using a transparent local estimate."
    if context.get("courses"):
        return f"Hi {user_label}, I found {context['courses']} active course enrollment(s) for you."
    return f"Hi {user_label}, ask about attendance, fees, assignments, GPA, materials, or university notices."


def generate_quiz_questions(source_text, count=5):
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if api_key:
        return [
            "Configured AI provider can generate richer questions here once live calls are enabled."
        ]

    seed = (source_text or "the uploaded lecture material").strip()
    topic = seed[:80].rstrip(".") or "the lecture material"
    return [
        f"Define the main concept discussed in {topic}.",
        f"List two practical applications of {topic}.",
        f"Explain why {topic} is important for students.",
        f"Compare {topic} with a related classroom concept.",
        f"Write a short note summarizing {topic}.",
    ][:count]
