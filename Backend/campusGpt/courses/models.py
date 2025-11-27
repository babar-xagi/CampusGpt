from django.db import models
from erp_login.models import StudentErpLogin, FacultyErpLogin


# ==================== SEMESTER ====================
class Semester(models.Model):
    """Semester model - Fall/Spring each year"""
    SEASON_CHOICES = (
        ('fall', 'Fall'),
        ('spring', 'Spring'),
    )
    
    season = models.CharField(max_length=10, choices=SEASON_CHOICES)
    year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('season', 'year')
        ordering = ['-year', 'season']
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'
    
    def __str__(self):
        return f"{self.get_season_display()} {self.year}"


# ==================== PROGRAM ====================
class Program(models.Model):
    """Program/Degree model - CS, Data Science, AI, etc."""
    PROGRAM_CHOICES = (
        ('bscs', 'BS Computer Science'),
        ('bsda', 'BS Data Science'),
        ('bsai', 'BS Artificial Intelligence'),
        ('bsse', 'BS Software Engineering'),
        ('bsit', 'BS Information Technology'),
    )
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    program_type = models.CharField(max_length=20, choices=PROGRAM_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


# ==================== COURSE ====================
class Course(models.Model):
    """Course model - individual courses in a program"""
    CREDIT_CHOICES = (
        (1, '1 Credit'),
        (2, '2 Credits'),
        (3, '3 Credits'),
        (4, '4 Credits'),
    )
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.IntegerField(choices=CREDIT_CHOICES, default=3)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('code', 'semester', 'program')
        ordering = ['program', 'semester', 'code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['semester']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ==================== CLASS ====================
class Class(models.Model):
    """Class/Section model - specific section of a course"""
    SECTION_CHOICES = (
        ('A', 'Section A'),
        ('B', 'Section B'),
        ('C', 'Section C'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    section = models.CharField(max_length=1, choices=SECTION_CHOICES)
    teacher = models.ForeignKey(FacultyErpLogin, on_delete=models.SET_NULL, null=True, related_name='classes')
    capacity = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('course', 'section')
        ordering = ['course', 'section']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
    
    def __str__(self):
        return f"{self.course.code} - Section {self.section}"
    
    def get_enrolled_count(self):
        """Get number of enrolled students"""
        return self.enrollments.filter(status='enrolled').count()


# ==================== ENROLLMENT ====================
class Enrollment(models.Model):
    """Enrollment model - student enrolled in a class"""
    STATUS_CHOICES = (
        ('enrolled', 'Enrolled'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
    )
    
    student = models.ForeignKey(StudentErpLogin, on_delete=models.CASCADE, related_name='enrollments')
    class_section = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'class_section')
        ordering = ['-enrollment_date']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['class_section']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.class_section.course.code}"
