from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import (
    Assignment,
    AttendanceRecord,
    CampusStaff,
    CourseMaterial,
    CourseSection,
    LeaveRequest,
    Notification,
)
from .services import answer_academic_question, generate_quiz_questions


@require_http_methods(["GET", "POST"])
def operations_staff_login(request):
    if request.user.is_authenticated and request.session.get("campus_role") == "operations_staff":
        return redirect("operations_staff_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        try:
            staff = CampusStaff.objects.get(username=username, is_active=True)
        except CampusStaff.DoesNotExist:
            messages.error(request, "Username not found")
        else:
            if staff.check_password(password):
                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={"email": staff.email, "is_staff": False, "is_superuser": False},
                )
                user.email = staff.email
                user.save()
                login(request, user)
                request.session["campus_role"] = "operations_staff"
                return redirect("operations_staff_dashboard")
            messages.error(request, "Invalid credentials")

    return render(request, "courses/operations_login.html")


@login_required(login_url="operations_staff_login")
@require_http_methods(["GET", "POST"])
def operations_staff_dashboard(request):
    if request.session.get("campus_role") != "operations_staff":
        return redirect("operations_staff_login")

    staff = get_object_or_404(CampusStaff, username=request.user.username, is_active=True)
    if request.method == "POST":
        LeaveRequest.objects.create(
            staff=staff,
            start_date=request.POST.get("start_date"),
            end_date=request.POST.get("end_date"),
            reason=request.POST.get("reason", ""),
        )
        messages.success(request, "Leave request submitted")
        return redirect("operations_staff_dashboard")

    context = {
        "staff": staff,
        "duties": staff.duties.select_related("staff")[:8],
        "attendance": staff.attendance.all()[:8],
        "salary_records": staff.salary_records.all()[:4],
        "leave_requests": staff.leave_requests.all()[:5],
        "notifications": Notification.objects.filter(user_username=staff.username)[:10],
    }
    return render(request, "courses/operations_dashboard.html", context)


@login_required
@require_http_methods(["POST"])
def ai_advisor(request):
    from django.http import JsonResponse
    import json

    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )

    role = request.session.get("campus_role", "student")
    question = request.POST.get("question", "")

    if not question and request.content_type == "application/json":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
        except json.JSONDecodeError:
            pass

    response = answer_academic_question(request.user.username, question)

    if is_ajax:
        return JsonResponse({"response": response})

    if role == "faculty":
        messages.info(request, response)
        return redirect("staff_dashboard")
    if role == "operations_staff":
        messages.info(request, response)
        return redirect("operations_staff_dashboard")
    messages.info(request, response)
    return redirect("student_dashboard")



@login_required(login_url="staff_login")
@require_http_methods(["POST"])
def mark_attendance(request, section_id):
    section = get_object_or_404(CourseSection, id=section_id, teacher__username=request.user.username)
    today = timezone.localdate()
    from .services import create_notification
    for enrollment in section.enrollments.filter(status="enrolled"):
        status = request.POST.get(f"attendance_{enrollment.id}", "present")
        AttendanceRecord.objects.update_or_create(
            enrollment=enrollment,
            date=today,
            defaults={"status": status, "marked_by": section.teacher},
        )
        if status in ["absent", "late"]:
            create_notification(
                username=enrollment.student.username,
                title=f"Attendance warning: {status.title()}",
                message=f"You were marked {status} in {section.course.code} on {today:%d %b %Y}.",
                category="attendance"
            )
    messages.success(request, f"Attendance saved for {section}")
    return redirect("staff_dashboard")


@login_required(login_url="staff_login")
@require_http_methods(["POST"])
def upload_material(request, section_id):
    section = get_object_or_404(CourseSection, id=section_id, teacher__username=request.user.username)
    title = request.POST.get("title", "Lecture material")
    CourseMaterial.objects.create(
        section=section,
        title=title,
        material_type=request.POST.get("material_type", "notes"),
        file=request.FILES.get("file"),
        external_url=request.POST.get("external_url", ""),
        uploaded_by=section.teacher,
    )
    from .services import create_notification
    for enrollment in section.enrollments.filter(status="enrolled"):
        create_notification(
            username=enrollment.student.username,
            title="New Course Material Uploaded",
            message=f"Professor {section.teacher.username} uploaded material '{title}' in {section.course.code}.",
            category="material"
        )
    messages.success(request, "Course material uploaded")
    return redirect("staff_dashboard")


@login_required(login_url="staff_login")
@require_http_methods(["POST"])
def generate_quiz(request, section_id):
    section = get_object_or_404(CourseSection, id=section_id, teacher__username=request.user.username)
    prompt = request.POST.get("source_text", section.course.name)
    questions = generate_quiz_questions(prompt)
    title = f"AI Quiz - {timezone.localdate():%d %b %Y}"
    Assignment.objects.create(
        section=section,
        title=title,
        assessment_type="quiz",
        description="\n".join(questions),
        total_marks=10,
    )
    from .services import create_notification
    for enrollment in section.enrollments.filter(status="enrolled"):
        create_notification(
            username=enrollment.student.username,
            title="New AI Quiz Generated",
            message=f"A new quiz '{title}' has been generated for {section.course.code}.",
            category="quiz"
        )
    messages.success(request, "AI quiz generated and saved")
    return redirect("staff_dashboard")
