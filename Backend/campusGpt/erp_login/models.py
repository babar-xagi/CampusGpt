from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import EmailValidator
from django.utils import timezone

# Create your models here.
#  HERE YOU CAN DEFINE MODELS FOR ERP LOGIN 
# -1 student Erp Login Model
"""
student email  is university provided email format: su92-bsdsm-001@superior.edu.pk
student username is their roll number = su92-bsdsm-001
student password is as he set during admission process 

these are the fields we need to store for erp login
- student username
- student email
- student password (hashed using Django's make_password)
- created_at (timestamp for audit)
- updated_at (timestamp for audit)
- is_active (to enable/disable accounts)
"""
class StudentErpLogin(models.Model):
    username = models.CharField(max_length=50, unique=True, help_text="University roll number")
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    password_hash = models.CharField(max_length=256, help_text="Hashed password")
    is_active = models.BooleanField(default=True, help_text="Inactive students cannot login")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "Student ERP Login"
        verbose_name_plural = "Student ERP Logins"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def set_password(self, raw_password):
        """Set password using Django's secure hashing"""
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verify password against hash"""
        return check_password(raw_password, self.password_hash)


# -2 Faculty Erp Login Model
"""
faculty email is university provided email format: ahmed@superior.edu.pk
faculty username is their official username = ahmed
faculty password is as he set during joining process

fields:
- faculty username
- faculty email
- faculty password (hashed using Django's make_password)
- is_active (to enable/disable accounts)
- created_at (timestamp for audit)
- updated_at (timestamp for audit)
"""
class FacultyErpLogin(models.Model):
    username = models.CharField(max_length=50, unique=True, help_text="Faculty official username")
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    password_hash = models.CharField(max_length=256, help_text="Hashed password")
    is_active = models.BooleanField(default=True, help_text="Inactive faculty cannot login")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "Faculty ERP Login"
        verbose_name_plural = "Faculty ERP Logins"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def set_password(self, raw_password):
        """Set password using Django's secure hashing"""
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verify password against hash"""
        return check_password(raw_password, self.password_hash)