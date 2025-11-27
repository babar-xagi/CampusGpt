# ERP Login App

## What Changed

### Models (erp_login/models.py)
- ✅ Added `is_active` field (BooleanField)
- ✅ Added `created_at` field (auto timestamp)
- ✅ Added `updated_at` field (auto timestamp)
- ✅ Added `set_password()` method - hashes password using PBKDF2
- ✅ Added `check_password()` method - verifies password
- ✅ Added database indexes on username and email

### Admin Panel (erp_login/admin.py)
- ✅ `StudentErpLoginAdmin` - Only superuser can access
- ✅ `FacultyErpLoginAdmin` - Superuser sees all, Staff sees only their own record
- ✅ Custom filters and display methods
- ✅ Read-only fields for security

### Settings (core/settings.py)
- ✅ Enhanced security settings (cookies, CSRF, XSS protection)
- ✅ Minimum password length: 12 characters

## Deleted

- ❌ Staff dashboard views
- ❌ `/admin/staff/` routes
- ❌ Staff templates
- ❌ `createsuperuser_staff` command
- ❌ Documentation files

## How to Use

### 1. Create Admin User

```bash
python manage.py createsuperuser

Username: admin
Email: admin@superior.edu.pk
Password: Admin@123456
```

### 2. Create Staff User (Via Admin Panel)

1. Go to: `http://127.0.0.1:8000/admin/`
2. Login as admin
3. Click "Faculty ERP Login" → "Add"
4. Fill details:
   - Username
   - Email
   - Password (will be hashed)
5. Save

### 3. Make User Staff

In admin panel:
1. Go to "Auth > Users"
2. Find the faculty user
3. Check "Staff status"
4. Save

### 4. Staff Login

- URL: `http://127.0.0.1:8000/admin/`
- Username: (faculty username)
- Password: (their password)
- Staff can only see their own record

## Database

Migrations applied:
- `0001_initial.py` - Initial models
- `0002_alter_*.py` - Added new fields and methods

Run: `python manage.py migrate`

## Files Modified

- `erp_login/models.py` - Added fields and methods
- `erp_login/admin.py` - Added role-based access control
- `core/settings.py` - Enhanced security
- `core/urls.py` - Added login and dashboard routes
- `erp_login/views.py` - Added login and dashboard views
- `templates/erp_login/` - Added login and dashboard templates

---

## 🎯 DEMO: Complete Workflow

### Step 1: Start Server

```bash
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000/`

---

### Step 2: Create Admin User (First Time Only)

```bash
python manage.py createsuperuser

Username: admin
Email: admin@superior.edu.pk
Password: Admin@123456
```

---

### Step 3: Add New Student in Admin Panel

#### 3.1 Go to Admin Panel

```
URL: http://127.0.0.1:8000/admin/
Username: admin
Password: Admin@123456
```

#### 3.2 Create Student

1. Click on **"Student ERP Login"** in left menu
2. Click **"Add Student ERP Login"** button
3. Fill the form:

```
Username: su92-bsdsm-001
Email: student1@superior.edu.pk
Password: student@123
Is Active: ✓ Check this
```

4. Click **"Save"** button

✅ **What happens automatically:**
- Student ERP Login record created
- Django User account created (is_staff=False)
- Student can now login

---

### Step 4: Student Login & Dashboard

#### 4.1 Go to Student Login Page

```
URL: http://127.0.0.1:8000/student/login/
```

#### 4.2 Enter Credentials

```
Roll Number / Username: su92-bsdsm-001
Password: student@123
```

#### 4.3 Click "Login" Button

✅ **Result:**
- Student redirected to: `http://127.0.0.1:8000/student/dashboard/`
- See profile information
- See account status (Active/Inactive)
- See access rights
- Can logout anytime

---

### Step 5: Add New Faculty/Staff in Admin Panel

#### 5.1 Go to Admin Panel (As Admin)

```
URL: http://127.0.0.1:8000/admin/
```

#### 5.2 Create Faculty

1. Click on **"Faculty ERP Login"** in left menu
2. Click **"Add Faculty ERP Login"** button
3. Fill the form:

```
Username: prof_ahmed
Email: ahmed@superior.edu.pk
Password: faculty@123
Is Active: ✓ Check this
```

4. Click **"Save"** button

✅ **What happens automatically:**
- Faculty ERP Login record created
- Django User account created with **is_staff=True**
- Faculty is now a staff member
- Can access both `/admin/` and `/staff/login/`

---

### Step 6: Staff/Faculty Login & Dashboard

#### 6.1 Go to Staff Login Page

```
URL: http://127.0.0.1:8000/staff/login/
```

#### 6.2 Enter Credentials

```
Username: prof_ahmed
Password: faculty@123
```

#### 6.3 Click "Login" Button

✅ **Result:**
- Faculty redirected to: `http://127.0.0.1:8000/staff/dashboard/`
- See faculty profile information
- See permissions (what they can and cannot do)
- See account creation date
- See last update time
- Can go to Admin Panel or logout

---

### Step 7: Admin Panel Access

#### 7.1 Admin View (Full Access)

```
URL: http://127.0.0.1:8000/admin/
```

**Admin can:**
- ✅ View all students
- ✅ View all faculty
- ✅ Edit all records
- ✅ Create new users
- ✅ Delete users
- ✅ Manage permissions

#### 7.2 Faculty View in Admin Panel (Limited Access)

If faculty logs into `http://127.0.0.1:8000/admin/`:
- ✅ See only their own faculty record
- ✅ Edit their own credentials
- ❌ Cannot see other faculty
- ❌ Cannot see students
- ❌ Cannot create/delete users

---

## 📋 Complete URLs Reference

```
Admin Panel:               http://127.0.0.1:8000/admin/
Student Login:            http://127.0.0.1:8000/student/login/
Student Dashboard:        http://127.0.0.1:8000/student/dashboard/
Faculty Login:            http://127.0.0.1:8000/staff/login/
Faculty Dashboard:        http://127.0.0.1:8000/staff/dashboard/
Logout:                   http://127.0.0.1:8000/logout/
Home:                     http://127.0.0.1:8000/
```

---

## 🔐 Security Features

✅ Passwords are hashed using PBKDF2-SHA256
✅ Each user can only access their own information
✅ Admin has full access
✅ Session-based authentication
✅ CSRF protection on all forms
✅ XSS protection enabled
✅ Secure cookies configured

---

## 🆘 Troubleshooting

### Student can't login

**Problem:** "Invalid credentials"

**Solution:**
1. Check if student record exists in admin panel
2. Verify username and password match exactly
3. Make sure "Is Active" is checked
4. Check that Django User was created (check Auth > Users)

### Faculty can't access admin panel

**Problem:** "You don't have permission to access this"

**Solution:**
1. Faculty must have "is_staff=True" in Django User
2. Create faculty via admin panel (auto-sets is_staff=True)
3. Verify in Auth > Users that staff checkbox is checked

### Password not working after creation

**Problem:** Can create user but can't login

**Solution:**
1. Password must be at least 8 characters
2. Make sure you saved the user (you'll see confirmation message)
3. Django User must exist in Auth > Users
4. Check that is_active is True

---

## 📊 User Types & Access Comparison

```
Feature              Admin    Student    Faculty
See own info         ✅       ✅         ✅
See other info       ✅       ❌         ❌
Edit own info        ✅       ✅         ✅
Edit other info      ✅       ❌         ❌
Access /admin/       ✅       ❌         ✅ (own)
Access /student/     ❌       ✅         ❌
Access /staff/       ❌       ❌         ✅
Create users         ✅       ❌         ❌
Delete users         ✅       ❌         ❌
```

---

## ✨ Summary

1. **Admin creates users** in `/admin/` panel
2. **Students login** at `/student/login/` → see `/student/dashboard/`
3. **Faculty login** at `/staff/login/` → see `/staff/dashboard/`
4. **All data is secure** - each user sees only their own info
5. **Django User auto-created** when you save ERP Login in admin
