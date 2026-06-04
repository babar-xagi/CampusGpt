# CampusGPT Django Backend Service

This directory contains the Django backend codebase, models, views, and services implementing the CampusGPT ERP.

## 📂 Directory Structure
*   `core/`: Core settings, security configs, and URL routing.
*   `courses/`: Models for courses, sections, enrollments, attendance records, notifications, salary records, leave requests, and staff duties. Also houses services (`services.py`) implementing GPA prediction, AI chatbot, and quiz generators.
*   `erp_login/`: Custom ERP models for student and faculty credentials, dashboards, and authentication checks.
*   `templates/`: HTML templates for landing pages, login panels, and dashboards.
*   `static/`: Assets, images, and custom stylesheets (specifically `static/css/modern.css` containing premium UI themes and animations).

## 🗄️ Database Models
1.  **StudentErpLogin / FacultyErpLogin:** Secure credentials storage with password hashing.
2.  **Course / CourseSection / Enrollment:** Section-specific capacity, course credits, and status tracking.
3.  **AttendanceRecord / GradeRecord:** Stores attendance logs and test marks.
4.  **Notification:** User notifications representing system events.
5.  **CampusStaff / StaffDuty / StaffAttendance / SalaryRecord / LeaveRequest:** Complete operational logistics models.

## 🛠️ Testing Backend Services
Verify correctness by running:
```bash
python manage.py test
```
This tests permissions, GPA accuracy, and authentication controls.
