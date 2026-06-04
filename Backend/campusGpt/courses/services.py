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
    total_weighted_points = 0
    total_credits = 0
    enrolled_count = 0
    graded_count = 0

    for enrollment in enrollments:
        enrolled_count += 1
        grades = list(enrollment.grade_records.all())
        credits = enrollment.section.course.credits or 3
        
        if not grades:
            continue
            
        graded_count += 1
        
        weighted_sum_percentage = sum(float(grade.percentage) * float(grade.weight) for grade in grades)
        sum_weights = sum(float(grade.weight) for grade in grades)
        
        if sum_weights > 0:
            course_percentage = weighted_sum_percentage / sum_weights
        else:
            course_percentage = sum(float(grade.percentage) for grade in grades) / len(grades)
            
        if course_percentage >= 85:
            gpa_point = 4.00
        elif course_percentage >= 80:
            gpa_point = 3.70
        elif course_percentage >= 75:
            gpa_point = 3.30
        elif course_percentage >= 70:
            gpa_point = 3.00
        elif course_percentage >= 65:
            gpa_point = 2.70
        elif course_percentage >= 61:
            gpa_point = 2.30
        elif course_percentage >= 58:
            gpa_point = 2.00
        elif course_percentage >= 55:
            gpa_point = 1.70
        elif course_percentage >= 50:
            gpa_point = 1.00
        else:
            gpa_point = 0.00
            
        total_weighted_points += gpa_point * credits
        total_credits += credits

    if total_credits == 0:
        return {
            "sgpa": 0.0,
            "cgpa": 0.0,
            "message": "Add course grades to enable GPA prediction forecasting."
        }

    sgpa = round(total_weighted_points / total_credits, 2)
    return {
        "sgpa": sgpa,
        "cgpa": sgpa,
        "message": f"Forecasted from {graded_count} of {enrolled_count} graded course section(s) weighted by credits."
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


def call_openai_chat_api(api_key, messages, model="gpt-4o-mini", temperature=0.7):
    import urllib.request
    import json
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error communicating with OpenAI: {str(e)}"


def get_user_db_context(username):
    context_str = ""
    user_type = "guest"
    
    try:
        from erp_login.models import StudentErpLogin
        student = StudentErpLogin.objects.get(username=username)
        enrollments = student.enrollments.filter(status='enrolled')
        user_type = "student"
        
        courses_info = []
        for e in enrollments:
            records = e.attendance_records.all()
            total = records.count()
            present = records.filter(status__in=["present", "late", "excused"]).count()
            pct = round((present / total) * 100, 2) if total else 100.0
            
            grades_info = [f"{g.title}: {g.obtained_marks}/{g.total_marks}" for g in e.grade_records.all()]
            grades_str = ", ".join(grades_info) if grades_info else "No grades recorded"
            
            courses_info.append(
                f"- {e.section.course.code} ({e.section.course.name}): Attendance {pct}% ({present}/{total}), Grades: {grades_str}"
            )
            
        courses_str = "\n".join(courses_info) if courses_info else "No active course enrollments."
        
        from courses.models import FeeRecord
        fees = FeeRecord.objects.filter(student=student)
        fees_info = [f"- {f.description}: Balance PKR {f.balance} (Status: {f.status}, Due: {f.due_date})" for f in fees]
        fees_str = "\n".join(fees_info) if fees_info else "No fee records."
        
        timetable_slots = []
        for e in enrollments:
            for slot in e.section.timetable_slots.all():
                timetable_slots.append(
                    f"- {slot.get_day_of_week_display()}: {slot.start_time}-{slot.end_time} in Room {slot.room} ({e.section.course.code})"
                )
        timetable_str = "\n".join(timetable_slots) if timetable_slots else "No timetable slots scheduled."
        
        context_str = (
            f"User: {username} (Student)\n\n"
            f"Active Courses & Attendance:\n{courses_str}\n\n"
            f"Fee Records:\n{fees_str}\n\n"
            f"Timetable slots:\n{timetable_str}"
        )
        return user_type, context_str
    except Exception:
        pass
        
    try:
        from erp_login.models import FacultyErpLogin
        faculty = FacultyErpLogin.objects.get(username=username)
        sections = faculty.sections.all()
        user_type = "faculty"
        
        sections_info = [
            f"- {s.course.code} Section {s.section} ({s.course.name}) in Room {s.room} ({s.enrolled_count()} students)"
            for s in sections
        ]
        sections_str = "\n".join(sections_info) if sections_info else "No assigned sections."
        
        context_str = f"User: {username} (Faculty)\n\nAssigned Course Sections:\n{sections_str}"
        return user_type, context_str
    except Exception:
        pass

    try:
        from courses.models import CampusStaff
        staff = CampusStaff.objects.get(username=username)
        duties = staff.duties.all()
        user_type = "staff"
        
        duties_info = [f"- {d.title} at {d.location} ({d.starts_at})" for d in duties]
        duties_str = "\n".join(duties_info) if duties_info else "No duties scheduled."
        
        context_str = f"User: {username} ({staff.get_role_display()})\n\nAssigned Duties:\n{duties_str}"
        return user_type, context_str
    except Exception:
        pass

    return user_type, f"User: {username}"


def answer_academic_question(user_label, question, context=None):
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    
    user_type, db_context = get_user_db_context(user_label)
    
    if api_key:
        system_prompt = (
            "You are CampusGPT, a premium AI academic advisor at Superior University.\n"
            "Below is the live database context of the currently logged-in user:\n"
            "======================\n"
            f"{db_context}\n"
            "======================\n"
            "Answer the user's questions clearly and professionally based on the context. "
            "If they ask about courses, attendance risk, or fee dues, reference the live data. "
            "If the question cannot be answered by the context, reply politely using standard campus guidelines."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        return call_openai_chat_api(api_key, messages)
        
    topic = (question or "").lower()
    
    if user_type == "student":
        if "attendance" in topic or "present" in topic or "absent" in topic:
            try:
                from erp_login.models import StudentErpLogin
                student = StudentErpLogin.objects.get(username=user_label)
                enrollments = student.enrollments.filter(status='enrolled')
                summaries = []
                for e in enrollments:
                    records = e.attendance_records.all()
                    total = records.count()
                    present = records.filter(status__in=["present", "late", "excused"]).count()
                    pct = round((present / total) * 100, 2) if total else 100.0
                    risk = "safe" if pct >= 80 else ("watch" if pct >= 70 else "danger")
                    summaries.append(f"{e.section.course.code} is at {pct}% ({risk})")
                return "Your live class attendance summary: " + (", ".join(summaries) if summaries else "no active enrollments found.") + ". Keep attendance at 80% or above to avoid risk alerts."
            except Exception:
                pass
            return "Your attendance is calculated dynamically. Try marking class slots to see risk warnings."
            
        if "fee" in topic or "due" in topic or "pay" in topic or "bill" in topic:
            try:
                from courses.models import FeeRecord
                from erp_login.models import StudentErpLogin
                student = StudentErpLogin.objects.get(username=user_label)
                fees = FeeRecord.objects.filter(student=student)
                summaries = [f"{f.description}: Balance PKR {f.balance} (Status: {f.status})" for f in fees]
                return "Your active invoice records: " + (", ".join(summaries) if summaries else "no outstanding bills.") + ". You can pay pending dues via the accounts office."
            except Exception:
                pass
            return "Fee details are managed on your dashboard. Please clear dues before midterms."
            
        if "gpa" in topic or "cgpa" in topic or "sgpa" in topic or "grade" in topic or "predict" in topic:
            try:
                from erp_login.models import StudentErpLogin
                student = StudentErpLogin.objects.get(username=user_label)
                pred = predict_sgpa(student.enrollments.filter(status='enrolled'))
                return f"Your forecasted SGPA is {pred['sgpa']}. {pred['message']}"
            except Exception:
                pass
            return "The forecasting engine projects your SGPA based on quiz and assignment marks."
            
        if "timetable" in topic or "class" in topic or "schedule" in topic or "time" in topic or "room" in topic:
            try:
                from erp_login.models import StudentErpLogin
                student = StudentErpLogin.objects.get(username=user_label)
                enrollments = student.enrollments.filter(status='enrolled')
                slots = []
                for e in enrollments:
                    for s in e.section.timetable_slots.all():
                        slots.append(f"{s.get_day_of_week_display()} {s.start_time}-{s.end_time} in Room {s.room} ({e.section.course.code})")
                return "Your scheduled timetable: " + (", ".join(slots) if slots else "no active slots found.")
            except Exception:
                pass
            return "Timetables are updated in real-time. Check Room assignments on your scheduler widget."
            
        return f"Hello {user_label}! I am your database-aware AI advisor. Ask me about your attendance risk, fee status, predicted GPA, or timetable."

    elif user_type == "faculty":
        if "student" in topic or "weak" in topic or "risk" in topic:
            return "As faculty, you can view academically at-risk students flagged under the Support section of your dashboard. They are identified based on attendance below 80% or grade average below 60%."
        if "section" in topic or "class" in topic or "course" in topic:
            try:
                from erp_login.models import FacultyErpLogin
                faculty = FacultyErpLogin.objects.get(username=user_label)
                sections = faculty.sections.all()
                sec_list = [f"{s.course.code} Section {s.section} ({s.enrolled_count()} enrolled)" for s in sections]
                return "Your assigned course sections: " + (", ".join(sec_list) if sec_list else "none.")
            except Exception:
                pass
            return "You can check assigned course outline sections directly from your homepage panel."
        return f"Hello Professor {user_label}! Ask me about student risk factors, section enrollments, or AI quiz configurations."

    elif user_type == "staff":
        return f"Hello {user_label}! You are signed in as campus operational staff. Ask me about assigned duties, salary payouts, or leave statuses."
        
    return f"Hello {user_label}! Ask about attendance, fees, assignments, GPA predictions, or class timetables."


def generate_quiz_questions(source_text, count=5):
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    
    if api_key:
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a university course coordinator. Generate a list of exactly {count} quiz questions "
                    "based on the provided lecture topic or notes. Format each question on a new line with clear labels."
                )
            },
            {"role": "user", "content": source_text}
        ]
        res = call_openai_chat_api(api_key, messages)
        if not res.startswith("Error"):
            return res.split("\n")
            
    seed = (source_text or "the uploaded lecture material").strip()
    topic = seed[:80].rstrip(".") or "the lecture material"
    return [
        f"Define the main concept discussed in {topic}.",
        f"List two practical applications of {topic}.",
        f"Explain why {topic} is important for students.",
        f"Compare {topic} with a related classroom concept.",
        f"Write a short note summarizing {topic}.",
    ][:count]


def create_notification(username, title, message, category="general"):
    try:
        from courses.models import Notification
        Notification.objects.create(
            user_username=username,
            title=title,
            message=message,
            category=category
        )
    except Exception as e:
        print(f"Error creating notification: {e}")


