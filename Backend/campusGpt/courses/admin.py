from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Announcement,
    Assignment,
    AttendanceRecord,
    CampusStaff,
    Course,
    CourseMaterial,
    CourseSection,
    Department,
    Enrollment,
    Event,
    FeeRecord,
    GradeRecord,
    LeaveRequest,
    Program,
    SalaryRecord,
    Semester,
    StaffAttendance,
    StaffDuty,
    TimetableSlot,
    Notification,
)



class CampusStaffForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Leave blank to keep existing password"}),
        help_text="Set or change the staff portal password.",
    )

    class Meta:
        model = CampusStaff
        fields = ("username", "email", "full_name", "role", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["password"].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("season", "year", "start_date", "end_date", "is_active")
    list_filter = ("season", "year", "is_active")


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "program_type", "department", "is_active")
    search_fields = ("name", "code")
    list_filter = ("program_type", "department", "is_active")


class TimetableInline(admin.TabularInline):
    model = TimetableSlot
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "program", "semester", "credits", "is_active")
    search_fields = ("code", "name")
    list_filter = ("program", "semester", "is_active")


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ("course", "section", "teacher", "room", "capacity", "is_active")
    search_fields = ("course__code", "course__name", "teacher__username")
    list_filter = ("course__semester", "section", "is_active")
    inlines = [TimetableInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "section", "status", "enrollment_date")
    search_fields = ("student__username", "section__course__code")
    list_filter = ("status", "section__course__semester")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "date", "status", "marked_by")
    list_filter = ("status", "date", "enrollment__section")
    search_fields = ("enrollment__student__username", "enrollment__section__course__code")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "assessment_type", "section", "due_at", "total_marks")
    list_filter = ("assessment_type", "section__course__semester")
    search_fields = ("title", "section__course__code")


@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "title", "obtained_marks", "total_marks", "percentage")
    search_fields = ("enrollment__student__username", "title")
    list_filter = ("enrollment__section",)


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "material_type", "section", "uploaded_by", "created_at")
    list_filter = ("material_type", "section__course__semester")
    search_fields = ("title", "section__course__code")


@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "description", "amount", "paid_amount", "balance", "status", "due_date")
    list_filter = ("status", "semester")
    search_fields = ("student__username", "description")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "section", "is_active", "created_at")
    list_filter = ("audience", "is_active", "created_at")
    search_fields = ("title", "body")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "starts_at", "location", "is_holiday")
    list_filter = ("is_holiday", "starts_at")
    search_fields = ("title", "location")


@admin.register(CampusStaff)
class CampusStaffAdmin(admin.ModelAdmin):
    form = CampusStaffForm
    list_display = ("full_name", "username", "email", "role", "status_badge")
    list_filter = ("role", "is_active")
    search_fields = ("full_name", "username", "email")
    readonly_fields = ("created_at", "updated_at", "password_status")

    fieldsets = (
        ("Profile", {"fields": ("full_name", "username", "email", "role")}),
        ("Login", {"fields": ("password", "password_status", "is_active")}),
        ("Audit", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def status_badge(self, obj):
        color = "green" if obj.is_active else "red"
        label = "Active" if obj.is_active else "Inactive"
        return format_html('<strong style="color: {};">{}</strong>', color, label)

    def password_status(self, obj):
        return "Password set" if obj.password_hash else "No password set"


@admin.register(StaffDuty)
class StaffDutyAdmin(admin.ModelAdmin):
    list_display = ("staff", "title", "location", "starts_at", "is_completed")
    list_filter = ("is_completed", "starts_at", "staff__role")
    search_fields = ("staff__username", "title", "location")


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ("staff", "date", "status", "check_in", "check_out")
    list_filter = ("status", "date", "staff__role")


@admin.register(SalaryRecord)
class SalaryRecordAdmin(admin.ModelAdmin):
    list_display = ("staff", "month", "gross_amount", "paid_amount", "paid_on")
    list_filter = ("month", "staff__role")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("staff", "start_date", "end_date", "status", "created_at")
    list_filter = ("status", "created_at", "staff__role")
    search_fields = ("staff__username", "reason")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user_username", "title", "category", "is_read", "created_at")
    list_filter = ("is_read", "category", "created_at")
    search_fields = ("user_username", "title", "message")

