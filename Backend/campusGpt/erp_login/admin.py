from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from django import forms
from .models import StudentErpLogin, FacultyErpLogin


# ==================== CUSTOM FORMS ====================
class StudentErpLoginForm(forms.ModelForm):
    """Custom form for Student ERP Login with password field"""
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Leave blank to keep existing password',
            'class': 'vTextField'
        }),
        help_text="Enter a password to set/change it. Leave blank to keep the existing password."
    )
    
    class Meta:
        model = StudentErpLogin
        fields = ('username', 'email', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password required only for new records
        if self.instance.pk:
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = "Enter a password for this student"
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        # Only update password if provided
        if password:
            instance.set_password(password)
        
        if commit:
            instance.save()
        return instance


class FacultyErpLoginForm(forms.ModelForm):
    """Custom form for Faculty ERP Login with password field"""
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Leave blank to keep existing password',
            'class': 'vTextField'
        }),
        help_text="Enter a password to set/change it. Leave blank to keep the existing password."
    )
    
    class Meta:
        model = FacultyErpLogin
        fields = ('username', 'email', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password required only for new records
        if self.instance.pk:
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = "Enter a password for this faculty member"
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        # Only update password if provided
        if password:
            instance.set_password(password)
        
        if commit:
            instance.save()
        return instance


# ==================== CUSTOM ADMIN FILTERS ====================
class IsActiveFilter(admin.SimpleListFilter):
    """Filter for active/inactive accounts"""
    title = 'Account Status'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)
        return queryset


# ==================== STUDENT ERP LOGIN ADMIN ====================
@admin.register(StudentErpLogin)
class StudentErpLoginAdmin(admin.ModelAdmin):
    """
    Admin interface for Student ERP Login credentials.
    - Only superusers can add/edit/delete
    - Staff can only view assigned records if configured
    - Displays password hash status instead of actual hash
    - Includes audit timestamps
    """
    
    form = StudentErpLoginForm
    list_display = ('username_display', 'email', 'is_active_status', 'created_at', 'updated_at')
    list_filter = (IsActiveFilter, 'created_at', 'is_active')
    search_fields = ('username', 'email')
    readonly_fields = ('created_at', 'updated_at', 'password_status')
    
    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'email', 'password', 'password_status')
        }),
        ('Account Status', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def username_display(self, obj):
        """Display username with ID for easy identification"""
        return f"{obj.username} (ID: {obj.id})"
    username_display.short_description = 'Username'

    def is_active_status(self, obj):
        """Display active status as colored badge"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
        )
    is_active_status.short_description = 'Status'

    def password_status(self, obj):
        """Display password hashing status instead of actual hash"""
        if obj.password_hash:
            return format_html(
                '<span style="color: green;">✓ Password Set (Hashed)</span>'
            )
        return format_html(
            '<span style="color: orange;">⚠ No Password Set</span>'
        )
    password_status.short_description = 'Password'

    def has_add_permission(self, request):
        """Only superusers can add"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Only superusers can edit"""
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        """Only superusers (admin) can view"""
        return request.user.is_superuser

    def get_queryset(self, request):
        """
        Only superusers can see student records.
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.none()
        return qs

    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically create Django User for student
        when a StudentErpLogin is created in admin panel
        """
        super().save_model(request, obj, form, change)
        
        # Create or update Django User automatically
        user, created = User.objects.get_or_create(
            username=obj.username,
            defaults={
                'email': obj.email,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        
        # If user already existed, update email
        if not created:
            user.email = obj.email
            user.save()


# ==================== FACULTY ERP LOGIN ADMIN ====================
@admin.register(FacultyErpLogin)
class FacultyErpLoginAdmin(admin.ModelAdmin):
    """
    Admin interface for Faculty ERP Login credentials.
    - Only superusers can manage all records
    - Staff (Faculty) can only view/edit their own credentials
    - Displays password hash status instead of actual hash
    - Includes audit timestamps
    """
    
    form = FacultyErpLoginForm
    list_display = ('username_display', 'email', 'is_active_status', 'created_at', 'updated_at')
    list_filter = (IsActiveFilter, 'created_at', 'is_active')
    search_fields = ('username', 'email')
    readonly_fields = ('created_at', 'updated_at', 'password_status')
    
    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'email', 'password', 'password_status')
        }),
        ('Account Status', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def username_display(self, obj):
        """Display username with ID for easy identification"""
        return f"{obj.username} (ID: {obj.id})"
    username_display.short_description = 'Username'

    def is_active_status(self, obj):
        """Display active status as colored badge"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
        )
    is_active_status.short_description = 'Status'

    def password_status(self, obj):
        """Display password hashing status instead of actual hash"""
        if obj.password_hash:
            return format_html(
                '<span style="color: green;">✓ Password Set (Hashed)</span>'
            )
        return format_html(
            '<span style="color: orange;">⚠ No Password Set</span>'
        )
    password_status.short_description = 'Password'

    # ==================== PERMISSIONS ====================
    def has_add_permission(self, request):
        """Only superusers can add"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Superusers edit all; faculty can edit only their own credentials"""
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return request.user.is_staff and obj.username == request.user.username

    def has_view_permission(self, request, obj=None):
        """Superusers view all; faculty can view only their own credentials"""
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return request.user.is_staff and obj.username == request.user.username

    def get_queryset(self, request):
        """
        Superusers see all faculty records; faculty see only their own record.
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(username=request.user.username)
        return qs

    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically create Django User for faculty
        when a FacultyErpLogin is created in admin panel
        """
        super().save_model(request, obj, form, change)
        
        # Create or update Django User automatically with is_staff=True
        user, created = User.objects.get_or_create(
            username=obj.username,
            defaults={
                'email': obj.email,
                'is_staff': True,
                'is_superuser': False,
            }
        )
        
        # If user already existed, update email and staff status
        if not created:
            user.email = obj.email
            user.is_staff = True
            user.save()


# ==================== ADMIN SITE CUSTOMIZATION ====================
admin.site.site_header = "Superior University ERP Login Admin"
admin.site.site_title = "Superior University ERP Login Admin Portal"
admin.site.index_title = "Welcome to Superior University ERP Login Admin Portal"

# Add custom admin site styling message
admin.site.site_url = None  # Remove "View site" link for security




