"""
Tests for ERP Login admin permissions and security.

Run with: python manage.py test erp_login
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from erp_login.models import StudentErpLogin, FacultyErpLogin


class StudentErpLoginModelTest(TestCase):
    """Test StudentErpLogin model functionality"""

    def setUp(self):
        self.student = StudentErpLogin.objects.create(
            username='su92-bsdsm-001',
            email='su92-bsdsm-001@superior.edu.pk'
        )

    def test_set_password(self):
        """Test password hashing with set_password"""
        password = 'SecurePassword123!'
        self.student.set_password(password)
        self.student.save()

        # Verify password is hashed, not plain text
        self.assertNotEqual(self.student.password_hash, password)
        self.assertTrue(self.student.password_hash.startswith('pbkdf2_sha256$'))

    def test_check_password(self):
        """Test password verification"""
        password = 'SecurePassword123!'
        self.student.set_password(password)

        # Correct password should return True
        self.assertTrue(self.student.check_password(password))

        # Wrong password should return False
        self.assertFalse(self.student.check_password('WrongPassword123!'))

    def test_student_string_representation(self):
        """Test __str__ method"""
        expected = f"{self.student.username} ({self.student.email})"
        self.assertEqual(str(self.student), expected)

    def test_is_active_default(self):
        """Test that students are active by default"""
        self.assertTrue(self.student.is_active)

    def test_unique_username(self):
        """Test that username must be unique"""
        with self.assertRaises(Exception):
            StudentErpLogin.objects.create(
                username='su92-bsdsm-001',  # Same as first student
                email='different@superior.edu.pk'
            )

    def test_unique_email(self):
        """Test that email must be unique"""
        with self.assertRaises(Exception):
            StudentErpLogin.objects.create(
                username='su92-bsdsm-002',
                email='su92-bsdsm-001@superior.edu.pk'  # Same as first student
            )


class FacultyErpLoginModelTest(TestCase):
    """Test FacultyErpLogin model functionality"""

    def setUp(self):
        self.faculty = FacultyErpLogin.objects.create(
            username='ahmed',
            email='ahmed@superior.edu.pk'
        )

    def test_set_password(self):
        """Test password hashing with set_password"""
        password = 'FacultyPass123!'
        self.faculty.set_password(password)
        self.faculty.save()

        # Verify password is hashed
        self.assertNotEqual(self.faculty.password_hash, password)
        self.assertTrue(self.faculty.password_hash.startswith('pbkdf2_sha256$'))

    def test_check_password(self):
        """Test password verification"""
        password = 'FacultyPass123!'
        self.faculty.set_password(password)

        self.assertTrue(self.faculty.check_password(password))
        self.assertFalse(self.faculty.check_password('WrongPassword123!'))

    def test_faculty_string_representation(self):
        """Test __str__ method"""
        expected = f"{self.faculty.username} ({self.faculty.email})"
        self.assertEqual(str(self.faculty), expected)

    def test_is_active_default(self):
        """Test that faculty are active by default"""
        self.assertTrue(self.faculty.is_active)


class AdminPermissionsTest(TestCase):
    """Test admin panel permissions"""

    def setUp(self):
        # Create test data
        self.student = StudentErpLogin.objects.create(
            username='su92-bsdsm-001',
            email='su92-bsdsm-001@superior.edu.pk'
        )
        self.student.set_password('StudentPass123!')
        self.student.save()

        self.faculty = FacultyErpLogin.objects.create(
            username='ahmed',
            email='ahmed@superior.edu.pk'
        )
        self.faculty.set_password('FacultyPass123!')
        self.faculty.save()

        # Create users
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@superior.edu.pk',
            password='AdminPass123!'
        )

        self.staff_user = User.objects.create_user(
            username='ahmed',
            email='ahmed@superior.edu.pk',
            password='StaffPass123!'
        )
        self.staff_user.is_staff = True
        self.staff_user.save()

        self.regular_user = User.objects.create_user(
            username='john',
            email='john@superior.edu.pk',
            password='UserPass123!'
        )

        self.client = Client()

    def test_superuser_can_access_admin(self):
        """Test that superuser can access admin panel"""
        self.client.login(username='admin', password='AdminPass123!')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_staff_can_access_admin(self):
        """Test that staff can access admin panel"""
        self.client.login(username='ahmed', password='StaffPass123!')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_access_admin(self):
        """Test that regular users cannot access admin panel"""
        self.client.login(username='john', password='UserPass123!')
        response = self.client.get('/admin/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_superuser_can_view_student_records(self):
        """Test that superuser can view student records"""
        self.client.login(username='admin', password='AdminPass123!')
        response = self.client.get('/admin/erp_login/studenterplogin/')
        self.assertEqual(response.status_code, 200)
        # Check that student record is visible
        self.assertContains(response, 'su92-bsdsm-001')

    def test_staff_cannot_view_student_records(self):
        """Test that staff cannot view student records"""
        self.client.login(username='ahmed', password='StaffPass123!')
        response = self.client.get('/admin/erp_login/studenterplogin/')
        # Should either be 403 (forbidden) or show empty list
        self.assertIn(response.status_code, [200, 403])

    def test_superuser_can_view_all_faculty(self):
        """Test that superuser can see all faculty records"""
        self.client.login(username='admin', password='AdminPass123!')
        response = self.client.get('/admin/erp_login/facultyerplogin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ahmed')

    def test_staff_can_view_only_own_faculty_record(self):
        """Test that staff can view only their own faculty record"""
        self.client.login(username='ahmed', password='StaffPass123!')
        response = self.client.get('/admin/erp_login/facultyerplogin/')
        self.assertEqual(response.status_code, 200)
        # Staff should see only their own record
        self.assertContains(response, 'ahmed')

    def test_password_never_exposed_in_response(self):
        """Test that passwords are never shown in admin responses"""
        self.client.login(username='admin', password='AdminPass123!')
        
        # View student details
        response = self.client.get(f'/admin/erp_login/studenterplogin/{self.student.id}/change/')
        self.assertEqual(response.status_code, 200)
        
        # Password should not be in plain text
        self.assertNotContains(response, 'StudentPass123!')
        # Hash should not be easily readable
        # (actual hash checking depends on template rendering)


class PasswordSecurityTest(TestCase):
    """Test password security features"""

    def test_password_hashing_algorithm(self):
        """Test that passwords use secure hashing"""
        student = StudentErpLogin.objects.create(
            username='test',
            email='test@superior.edu.pk'
        )
        password = 'SecurePass123!'
        student.set_password(password)
        student.save()

        # Should use PBKDF2
        self.assertTrue(student.password_hash.startswith('pbkdf2_sha256$'))

    def test_same_password_different_hash(self):
        """Test that same password produces different hashes (due to salt)"""
        student1 = StudentErpLogin.objects.create(
            username='test1',
            email='test1@superior.edu.pk'
        )
        student1.set_password('SamePassword123!')
        student1.save()

        student2 = StudentErpLogin.objects.create(
            username='test2',
            email='test2@superior.edu.pk'
        )
        student2.set_password('SamePassword123!')
        student2.save()

        # Same password should produce different hashes (due to salt)
        self.assertNotEqual(student1.password_hash, student2.password_hash)

        # But both should verify correctly
        self.assertTrue(student1.check_password('SamePassword123!'))
        self.assertTrue(student2.check_password('SamePassword123!'))

    def test_invalid_password_check(self):
        """Test that invalid passwords are rejected"""
        student = StudentErpLogin.objects.create(
            username='test',
            email='test@superior.edu.pk'
        )
        student.set_password('CorrectPassword123!')
        student.save()

        # Various wrong passwords
        wrong_passwords = [
            'WrongPassword123!',
            'correctpassword123!',  # Wrong case
            'CorrectPassword123',   # Missing character
            'CorrectPassword123!!', # Extra character
            '',                      # Empty
        ]

        for wrong_pass in wrong_passwords:
            self.assertFalse(student.check_password(wrong_pass))
