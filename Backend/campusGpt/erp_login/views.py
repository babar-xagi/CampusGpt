from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import StudentErpLogin, FacultyErpLogin
from courses.models import Announcement, Event, FeeRecord
from courses.services import predict_sgpa, student_attendance_overview, weak_student_rows


@require_http_methods(["GET", "POST"])
def staff_login(request):
    """Staff (Faculty) login page"""
    # If already logged in as staff (not admin), redirect to dashboard
    if request.user.is_authenticated and request.user.is_staff and not request.user.is_superuser:
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        # Check in FacultyErpLogin
        try:
            faculty = FacultyErpLogin.objects.get(username=username)
            if faculty.check_password(password) and faculty.is_active:
                # Create/update Django user for session
                from django.contrib.auth.models import User
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': faculty.email,
                        'is_staff': True,
                        'is_superuser': False,
                    }
                )
                # Ensure user is staff
                if not user.is_staff:
                    user.is_staff = True
                    user.save()
                
                login(request, user)
                request.session['campus_role'] = 'faculty'
                return redirect('staff_dashboard')
            else:
                messages.error(request, '❌ Invalid credentials')
        except FacultyErpLogin.DoesNotExist:
            messages.error(request, '❌ Username not found')
    
    return render(request, 'erp_login/staff_login.html')


@require_http_methods(["GET", "POST"])
def student_login(request):
    """Student login page"""
    # If already logged in as student (not staff), redirect to dashboard
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        # Check in StudentErpLogin
        try:
            student = StudentErpLogin.objects.get(username=username)
            if student.check_password(password) and student.is_active:
                # Create/update Django user for session
                from django.contrib.auth.models import User
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': student.email,
                        'is_staff': False,
                        'is_superuser': False,
                    }
                )
                login(request, user)
                request.session['campus_role'] = 'student'
                return redirect('student_dashboard')
            else:
                messages.error(request, '❌ Invalid credentials')
        except StudentErpLogin.DoesNotExist:
            messages.error(request, '❌ Username not found')
    
    return render(request, 'erp_login/student_login.html')


@login_required(login_url='staff_login')
def staff_dashboard(request):
    """Staff dashboard - shows their own faculty record"""
    if not request.user.is_staff or request.user.is_superuser:
        return redirect('staff_login')
    
    try:
        faculty = FacultyErpLogin.objects.get(username=request.user.username)
    except FacultyErpLogin.DoesNotExist:
        messages.error(request, 'Faculty record not found')
        return redirect('staff_login')
    
    sections = faculty.sections.select_related('course', 'course__semester', 'course__program').prefetch_related(
        'enrollments__student',
        'enrollments__attendance_records',
        'enrollments__grade_records',
        'assignments',
        'materials',
    )
    weak_students = []
    for section in sections:
        weak_students.extend(weak_student_rows(section))

    context = {
        'faculty': faculty,
        'sections': sections,
        'announcements': Announcement.objects.filter(audience__in=['all', 'teachers'], is_active=True)[:5],
        'weak_students': weak_students[:8],
        'page_title': f'Faculty Dashboard - {faculty.username}',
    }
    
    return render(request, 'erp_login/staff_dashboard.html', context)


@login_required(login_url='student_login')
def student_dashboard(request):
    """Student dashboard - shows their own student record"""
    if request.user.is_staff:
        return redirect('student_login')
    
    try:
        student = StudentErpLogin.objects.get(username=request.user.username)
    except StudentErpLogin.DoesNotExist:
        messages.error(request, 'Student record not found')
        return redirect('student_login')
    
    enrollments = student.enrollments.select_related(
        'section',
        'section__course',
        'section__course__semester',
        'section__teacher',
    ).prefetch_related(
        'attendance_records',
        'grade_records',
        'section__assignments',
        'section__materials',
        'section__timetable_slots',
    ).filter(status='enrolled')
    sections = [enrollment.section for enrollment in enrollments]
    assignments = []
    materials = []
    timetable_slots = []
    for section in sections:
        assignments.extend(section.assignments.all())
        materials.extend(section.materials.all())
        timetable_slots.extend(section.timetable_slots.all())

    context = {
        'student': student,
        'enrollments': enrollments,
        'attendance_rows': student_attendance_overview(enrollments),
        'prediction': predict_sgpa(enrollments),
        'assignments': sorted(assignments, key=lambda item: item.due_at or item.created_at)[:8],
        'materials': sorted(materials, key=lambda item: item.created_at, reverse=True)[:8],
        'timetable_slots': sorted(timetable_slots, key=lambda item: (item.day_of_week, item.start_time))[:10],
        'fee_records': FeeRecord.objects.filter(student=student)[:8],
        'announcements': Announcement.objects.filter(audience__in=['all', 'students'], is_active=True)[:5],
        'events': Event.objects.all()[:5],
        'page_title': f'Student Dashboard - {student.username}',
    }
    
    return render(request, 'erp_login/student_dashboard.html', context)


@require_http_methods(["GET"])
def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('home')

