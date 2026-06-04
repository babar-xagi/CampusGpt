from django.contrib.auth.hashers import check_password, make_password
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from erp_login.models import FacultyErpLogin, StudentErpLogin


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Semester(models.Model):
    SEASON_CHOICES = (
        ("fall", "Fall"),
        ("spring", "Spring"),
        ("summer", "Summer"),
    )

    season = models.CharField(max_length=10, choices=SEASON_CHOICES)
    year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("season", "year")
        ordering = ["-year", "season"]

    def __str__(self):
        return f"{self.get_season_display()} {self.year}"


class Program(models.Model):
    PROGRAM_CHOICES = (
        ("bscs", "BS Computer Science"),
        ("bsds", "BS Data Science"),
        ("bsai", "BS Artificial Intelligence"),
        ("bsse", "BS Software Engineering"),
        ("bsit", "BS Information Technology"),
    )

    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="programs", null=True, blank=True
    )
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    program_type = models.CharField(max_length=20, choices=PROGRAM_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    CREDIT_CHOICES = ((1, "1 Credit"), (2, "2 Credits"), (3, "3 Credits"), (4, "4 Credits"))

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveSmallIntegerField(choices=CREDIT_CHOICES, default=3)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="courses")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="courses")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("code", "semester", "program")
        ordering = ["program", "semester", "code"]
        indexes = [models.Index(fields=["code"]), models.Index(fields=["semester"])]

    def __str__(self):
        return f"{self.code} - {self.name}"


class CourseSection(models.Model):
    SECTION_CHOICES = (("A", "Section A"), ("B", "Section B"), ("C", "Section C"))

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    section = models.CharField(max_length=1, choices=SECTION_CHOICES)
    teacher = models.ForeignKey(
        FacultyErpLogin, on_delete=models.SET_NULL, null=True, blank=True, related_name="sections"
    )
    room = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("course", "section")
        ordering = ["course", "section"]

    def __str__(self):
        return f"{self.course.code} - Section {self.section}"

    def enrolled_count(self):
        return self.enrollments.filter(status="enrolled").count()


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ("enrolled", "Enrolled"),
        ("dropped", "Dropped"),
        ("completed", "Completed"),
    )

    student = models.ForeignKey(StudentErpLogin, on_delete=models.CASCADE, related_name="enrollments")
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="enrolled")
    enrollment_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "section")
        ordering = ["-enrollment_date"]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["section"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.section.course.code}"


class TimetableSlot(models.Model):
    DAY_CHOICES = (
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    )

    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="timetable_slots")
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        unique_together = ("section", "day_of_week", "start_time")

    def __str__(self):
        return f"{self.section} {self.get_day_of_week_display()} {self.start_time}"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    )

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(
        FacultyErpLogin, on_delete=models.SET_NULL, null=True, blank=True, related_name="marked_attendance"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("enrollment", "date")
        ordering = ["-date"]
        indexes = [models.Index(fields=["date", "status"])]

    def __str__(self):
        return f"{self.enrollment} - {self.date} - {self.status}"


class Assignment(models.Model):
    TYPE_CHOICES = (("assignment", "Assignment"), ("quiz", "Quiz"))

    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=180)
    assessment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="assignment")
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_at", "title"]

    def __str__(self):
        return f"{self.title} ({self.section})"


class GradeRecord(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="grade_records")
    assignment = models.ForeignKey(
        Assignment, on_delete=models.SET_NULL, null=True, blank=True, related_name="grade_records"
    )
    title = models.CharField(max_length=160)
    obtained_marks = models.DecimalField(max_digits=6, decimal_places=2)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    @property
    def percentage(self):
        if not self.total_marks:
            return 0
        return float((self.obtained_marks / self.total_marks) * 100)

    def __str__(self):
        return f"{self.enrollment} - {self.title}"


class CourseMaterial(models.Model):
    MATERIAL_CHOICES = (
        ("slides", "Slides"),
        ("notes", "Notes"),
        ("pdf", "PDF"),
        ("link", "External Link"),
    )

    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=180)
    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default="notes")
    file = models.FileField(upload_to="course_materials/", blank=True)
    external_url = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(
        FacultyErpLogin, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_materials"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.section})"


class FeeRecord(models.Model):
    STATUS_CHOICES = (("paid", "Paid"), ("partial", "Partial"), ("due", "Due"))

    student = models.ForeignKey(StudentErpLogin, on_delete=models.CASCADE, related_name="fee_records")
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=180)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="due")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "due_date"]

    @property
    def balance(self):
        return self.amount - self.paid_amount

    def __str__(self):
        return f"{self.student.username} - {self.description}"


class Announcement(models.Model):
    AUDIENCE_CHOICES = (
        ("all", "Everyone"),
        ("students", "Students"),
        ("teachers", "Teachers"),
        ("staff", "Operational Staff"),
    )

    title = models.CharField(max_length=180)
    body = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default="all")
    section = models.ForeignKey(
        CourseSection, on_delete=models.CASCADE, related_name="announcements", null=True, blank=True
    )
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=120, blank=True)
    is_holiday = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return self.title


class CampusStaff(models.Model):
    ROLE_CHOICES = (
        ("guard", "Guard"),
        ("librarian", "Librarian"),
        ("lab_assistant", "Lab Assistant"),
        ("office_assistant", "Office Assistant"),
        ("sweeper", "Sweeper"),
    )

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    password_hash = models.CharField(max_length=256)
    full_name = models.CharField(max_length=120)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)


class StaffDuty(models.Model):
    staff = models.ForeignKey(CampusStaff, on_delete=models.CASCADE, related_name="duties")
    title = models.CharField(max_length=160)
    location = models.CharField(max_length=120, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return f"{self.staff.username} - {self.title}"


class StaffAttendance(models.Model):
    STATUS_CHOICES = (("present", "Present"), ("absent", "Absent"), ("late", "Late"))

    staff = models.ForeignKey(CampusStaff, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("staff", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.staff.username} - {self.date} - {self.status}"


class SalaryRecord(models.Model):
    staff = models.ForeignKey(CampusStaff, on_delete=models.CASCADE, related_name="salary_records")
    month = models.DateField(help_text="Use the first day of the salary month")
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_on = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("staff", "month")
        ordering = ["-month"]

    def __str__(self):
        return f"{self.staff.username} salary {self.month:%b %Y}"


class LeaveRequest(models.Model):
    STATUS_CHOICES = (("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"))

    staff = models.ForeignKey(CampusStaff, on_delete=models.CASCADE, related_name="leave_requests")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.staff.username} leave {self.start_date}"


class Notification(models.Model):
    user_username = models.CharField(max_length=150, db_index=True)
    title = models.CharField(max_length=180)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    category = models.CharField(max_length=30, default="general")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_username} - {self.title} - {self.is_read}"

