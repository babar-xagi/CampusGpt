from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from erp_login.models import FacultyErpLogin, StudentErpLogin
from .models import (
    Assignment,
    AttendanceRecord,
    CampusStaff,
    Course,
    CourseSection,
    Department,
    Enrollment,
    GradeRecord,
    Program,
    Semester,
    TimetableSlot,
)
from .services import attendance_summary, generate_quiz_questions, predict_sgpa


class CampusMvpDataMixin:
    def setUp(self):
        self.student = StudentErpLogin.objects.create(
            username="su92-bsdsm-001", email="su92-bsdsm-001@superior.edu.pk"
        )
        self.student.set_password("StudentPass123!")
        self.student.save()

        self.faculty = FacultyErpLogin.objects.create(username="ahmed", email="ahmed@superior.edu.pk")
        self.faculty.set_password("FacultyPass123!")
        self.faculty.save()

        self.department = Department.objects.create(name="Computer Science", code="CS")
        self.program = Program.objects.create(
            department=self.department,
            code="BSDS",
            name="BS Data Science",
            program_type="bsds",
        )
        self.semester = Semester.objects.create(
            season="fall",
            year=2026,
            start_date=date(2026, 9, 1),
            end_date=date(2027, 1, 15),
        )
        self.course = Course.objects.create(
            code="DS301",
            name="Machine Learning",
            credits=3,
            semester=self.semester,
            program=self.program,
        )
        self.section = CourseSection.objects.create(
            course=self.course, section="A", teacher=self.faculty, room="Lab 3"
        )
        self.enrollment = Enrollment.objects.create(student=self.student, section=self.section)
        TimetableSlot.objects.create(
            section=self.section,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(10, 30),
            room="Lab 3",
        )


class AcademicModelTest(CampusMvpDataMixin, TestCase):
    def test_enrollment_string_and_count(self):
        self.assertIn("su92-bsdsm-001", str(self.enrollment))
        self.assertEqual(self.section.enrolled_count(), 1)

    def test_attendance_risk_calculation(self):
        today = timezone.localdate()
        statuses = ["present", "absent", "present", "late"]
        for index, status in enumerate(statuses):
            AttendanceRecord.objects.create(
                enrollment=self.enrollment,
                date=today - timedelta(days=index),
                status=status,
                marked_by=self.faculty,
            )
        summary = attendance_summary(self.enrollment)
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["present"], 3)
        self.assertEqual(summary["percentage"], 75)
        self.assertEqual(summary["risk"], "watch")

    def test_sgpa_prediction_fallback(self):
        assignment = Assignment.objects.create(section=self.section, title="Quiz 1", total_marks=10)
        GradeRecord.objects.create(
            enrollment=self.enrollment,
            assignment=assignment,
            title="Quiz 1",
            obtained_marks=Decimal("8"),
            total_marks=Decimal("10"),
        )
        prediction = predict_sgpa([self.enrollment])
        self.assertEqual(prediction["sgpa"], 3.7)


    def test_quiz_generation_fallback(self):
        questions = generate_quiz_questions("linear regression and model evaluation")
        self.assertEqual(len(questions), 5)
        self.assertIn("linear regression", questions[0])


class DashboardAccessTest(CampusMvpDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.student_user = User.objects.create_user(
            username=self.student.username, email=self.student.email, password="StudentPass123!"
        )
        self.faculty_user = User.objects.create_user(
            username=self.faculty.username, email=self.faculty.email, password="FacultyPass123!", is_staff=True
        )
        self.staff = CampusStaff.objects.create(
            username="lib_aslam",
            email="lib_aslam@superior.edu.pk",
            full_name="Aslam Khan",
            role="librarian",
        )
        self.staff.set_password("StaffPass123!")
        self.staff.save()
        self.client = Client()

    def test_student_dashboard_smoke(self):
        self.client.force_login(self.student_user)
        response = self.client.get("/student/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Hub")
        self.assertContains(response, "Machine Learning")


    def test_faculty_dashboard_smoke(self):
        self.client.force_login(self.faculty_user)
        response = self.client.get("/staff/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Faculty Dashboard")
        self.assertContains(response, "Machine Learning")

    def test_operations_staff_login_and_dashboard(self):
        response = self.client.post(
            "/operations/login/",
            {"username": "lib_aslam", "password": "StaffPass123!"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Operational Staff Dashboard")

    def test_ai_advisor_redirects_for_student(self):
        self.client.force_login(self.student_user)
        response = self.client.post("/ai/advisor/", {"question": "How is my attendance?"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/student/dashboard/")
