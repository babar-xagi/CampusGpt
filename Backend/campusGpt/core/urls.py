"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from views import (
    home,
)
from erp_login.views import (
    staff_login,
    student_login,
    staff_dashboard,
    student_dashboard,
    logout_view,
)
from courses import views as course_views


urlpatterns = [
    # Admin Panel
    path("admin/", admin.site.urls, name="admin"),
    
    # Login Pages
    path("staff/login/", staff_login, name="staff_login"),
    path("student/login/", student_login, name="student_login"),
    path("logout/", logout_view, name="logout"),
    
    # Dashboards
    path("staff/dashboard/", staff_dashboard, name="staff_dashboard"),
    path("student/dashboard/", student_dashboard, name="student_dashboard"),
    path("operations/login/", course_views.operations_staff_login, name="operations_staff_login"),
    path("operations/dashboard/", course_views.operations_staff_dashboard, name="operations_staff_dashboard"),
    path("ai/advisor/", course_views.ai_advisor, name="ai_advisor"),
    path("teacher/attendance/<int:section_id>/", course_views.mark_attendance, name="mark_attendance"),
    path("teacher/materials/<int:section_id>/", course_views.upload_material, name="upload_material"),
    path("teacher/quiz/<int:section_id>/", course_views.generate_quiz, name="generate_quiz"),
    
    # Home page
    path("", home, name="home"),
    
    # Temporary placeholder routes for missing views
    path("admission/", home, name="admission_main"),
    path("login/", student_login, name="login"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
