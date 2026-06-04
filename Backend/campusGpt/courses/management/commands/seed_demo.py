from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from erp_login.models import FacultyErpLogin, StudentErpLogin
from courses.models import (
    Announcement,
    Assignment,
    AttendanceRecord,
    CampusStaff,
    Course,
    CourseSection,
    Department,
    Enrollment,
    Event,
    FeeRecord,
    GradeRecord,
    Program,
    SalaryRecord,
    Semester,
    StaffAttendance,
    StaffDuty,
    TimetableSlot,
)


class Command(BaseCommand):
    help = "Seed CampusGPT with demo ERP data for the Django MVP"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CampusGPT demo data...")

        from django.contrib.auth.models import User
        if not User.objects.filter(username="admin", is_superuser=True).exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@superior.edu.pk",
                password="AdminPass123!"
            )
            self.stdout.write("Superuser 'admin' created.")


        student, _ = StudentErpLogin.objects.get_or_create(
            username="su92-bsdsm-001",
            defaults={"email": "su92-bsdsm-001@superior.edu.pk"},
        )
        student.set_password("StudentPass123!")
        student.save()

        faculty, _ = FacultyErpLogin.objects.get_or_create(
            username="ahmed",
            defaults={"email": "ahmed@superior.edu.pk"},
        )
        faculty.set_password("FacultyPass123!")
        faculty.save()

        department, _ = Department.objects.get_or_create(
            code="FCIT", defaults={"name": "Faculty of Computer Science"}
        )
        program, _ = Program.objects.get_or_create(
            code="BSDS",
            defaults={
                "name": "BS Data Science",
                "program_type": "bsds",
                "department": department,
            },
        )
        semester, _ = Semester.objects.get_or_create(
            season="fall",
            year=2026,
            defaults={"start_date": date(2026, 9, 1), "end_date": date(2027, 1, 15)},
        )
        course, _ = Course.objects.get_or_create(
            code="DS301",
            semester=semester,
            program=program,
            defaults={"name": "Machine Learning", "credits": 3},
        )
        section, _ = CourseSection.objects.get_or_create(
            course=course,
            section="A",
            defaults={"teacher": faculty, "room": "Lab 3", "capacity": 45},
        )
        enrollment, _ = Enrollment.objects.get_or_create(student=student, section=section)

        TimetableSlot.objects.get_or_create(
            section=section,
            day_of_week=0,
            start_time=time(9, 0),
            defaults={"end_time": time(10, 30), "room": "Lab 3"},
        )
        TimetableSlot.objects.get_or_create(
            section=section,
            day_of_week=2,
            start_time=time(11, 0),
            defaults={"end_time": time(12, 30), "room": "Room 204"},
        )

        for offset, status in enumerate(["present", "present", "absent", "late", "present"]):
            AttendanceRecord.objects.update_or_create(
                enrollment=enrollment,
                date=timezone.localdate() - timedelta(days=offset),
                defaults={"status": status, "marked_by": faculty},
            )

        assignment, _ = Assignment.objects.get_or_create(
            section=section,
            title="Regression Practice Quiz",
            defaults={
                "assessment_type": "quiz",
                "description": "Solve short questions on regression basics.",
                "due_at": timezone.now() + timedelta(days=5),
                "total_marks": Decimal("10"),
            },
        )
        GradeRecord.objects.get_or_create(
            enrollment=enrollment,
            title="Quiz 1",
            defaults={
                "assignment": assignment,
                "obtained_marks": Decimal("7.5"),
                "total_marks": Decimal("10"),
            },
        )

        FeeRecord.objects.get_or_create(
            student=student,
            semester=semester,
            description="Fall 2026 tuition",
            defaults={
                "amount": Decimal("85000"),
                "paid_amount": Decimal("50000"),
                "due_date": timezone.localdate() + timedelta(days=20),
                "status": "partial",
            },
        )
        Announcement.objects.get_or_create(
            title="Midterm schedule published",
            defaults={"body": "Check your dashboard for upcoming assessment dates.", "audience": "all"},
        )
        Event.objects.get_or_create(
            title="AI in Education Seminar",
            defaults={
                "description": "Guest session for FCIT students.",
                "starts_at": timezone.now() + timedelta(days=10),
                "location": "Auditorium",
            },
        )

        staff, _ = CampusStaff.objects.get_or_create(
            username="lib_aslam",
            defaults={
                "email": "lib_aslam@superior.edu.pk",
                "full_name": "Aslam Khan",
                "role": "librarian",
            },
        )
        staff.set_password("StaffPass123!")
        staff.save()
        StaffDuty.objects.get_or_create(
            staff=staff,
            title="Library evening desk",
            starts_at=timezone.make_aware(datetime.combine(timezone.localdate(), time(15, 0))),
            defaults={"ends_at": timezone.make_aware(datetime.combine(timezone.localdate(), time(21, 0))), "location": "Central Library"},
        )
        StaffAttendance.objects.update_or_create(
            staff=staff,
            date=timezone.localdate(),
            defaults={"status": "present", "check_in": time(8, 55)},
        )
        SalaryRecord.objects.get_or_create(
            staff=staff,
            month=date(timezone.localdate().year, timezone.localdate().month, 1),
            defaults={"gross_amount": Decimal("45000"), "paid_amount": Decimal("45000"), "paid_on": timezone.localdate()},
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write("Admin Superuser: admin / AdminPass123!")
        self.stdout.write("Student: su92-bsdsm-001 / StudentPass123!")
        self.stdout.write("Faculty: ahmed / FacultyPass123!")
        self.stdout.write("Operational staff: lib_aslam / StaffPass123!")
