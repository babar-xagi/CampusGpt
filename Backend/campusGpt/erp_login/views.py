from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import StudentErpLogin, FacultyErpLogin


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
    
    context = {
        'faculty': faculty,
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
    
    context = {
        'student': student,
        'page_title': f'Student Dashboard - {student.username}',
    }
    
    return render(request, 'erp_login/student_dashboard.html', context)


@require_http_methods(["GET"])
def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('home')

