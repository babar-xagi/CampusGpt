"""
Management command to create test student and faculty credentials with proper password hashing.

Usage:
    python manage.py create_test_credentials
"""

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from erp_login.models import StudentErpLogin, FacultyErpLogin


class Command(BaseCommand):
    help = 'Create test student and faculty ERP login credentials'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test credentials...\n'))

        # Test Student Credentials
        students_data = [
            {
                'username': 'su92-bsdsm-001',
                'email': 'su92-bsdsm-001@superior.edu.pk',
                'password': 'StudentPass123!',
            },
            {
                'username': 'su92-bsdsm-002',
                'email': 'su92-bsdsm-002@superior.edu.pk',
                'password': 'StudentPass123!',
            },
        ]

        for student_data in students_data:
            try:
                student = StudentErpLogin.objects.create(
                    username=student_data['username'],
                    email=student_data['email'],
                )
                student.set_password(student_data['password'])
                student.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Student created: {student_data["username"]}')
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Student already exists: {student_data["username"]}')
                )

        # Test Faculty Credentials
        faculty_data = [
            {
                'username': 'ahmed',
                'email': 'ahmed@superior.edu.pk',
                'password': 'FacultyPass123!',
            },
            {
                'username': 'maria',
                'email': 'maria@superior.edu.pk',
                'password': 'FacultyPass123!',
            },
        ]

        for faculty_info in faculty_data:
            try:
                faculty = FacultyErpLogin.objects.create(
                    username=faculty_info['username'],
                    email=faculty_info['email'],
                )
                faculty.set_password(faculty_info['password'])
                faculty.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Faculty created: {faculty_info["username"]}')
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Faculty already exists: {faculty_info["username"]}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Test credentials created successfully!')
        )
        self.stdout.write('\nTest Credentials:')
        self.stdout.write('─' * 60)
        self.stdout.write('\nStudents:')
        for student in students_data:
            self.stdout.write(f'  Username: {student["username"]}')
            self.stdout.write(f'  Password: {student["password"]}\n')

        self.stdout.write('Faculty:')
        for faculty in faculty_data:
            self.stdout.write(f'  Username: {faculty["username"]}')
            self.stdout.write(f'  Password: {faculty["password"]}\n')

        self.stdout.write(self.style.WARNING(
            '\n⚠ Remember to change these passwords in production!'
        ))
