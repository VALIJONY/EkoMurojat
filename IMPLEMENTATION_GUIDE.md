# EkoMurojat - Implementation Guide

## Overview
Complete Django-based environmental complaint management system with role-based access control.

## Tech Stack
- **Backend**: Django 4.x + Django REST Framework
- **Views**: Django Class-Based Views (CBV)
- **Frontend**: Django Templates (HTML + CSS)
- **Auth**: Django authentication with custom roles
- **Database**: PostgreSQL with PostGIS

## Project Structure

```
EkoMurojat/
├── complaints/
│   ├── forms.py          # All form classes
│   ├── views.py          # Class-Based Views for all roles
│   ├── urls.py           # URL routing
│   └── models.py         # Existing models (unchanged)
├── templates/
│   ├── base.html         # Base template with navigation
│   └── complaints/
│       ├── user_dashboard.html
│       ├── user_complaint_list.html
│       ├── user_complaint_detail.html
│       ├── user_complaint_create.html
│       ├── user_complaint_confirm_delete.html
│       ├── user_profile.html
│       ├── admin_dashboard.html
│       ├── admin_complaint_list.html
│       ├── admin_complaint_detail.html
│       ├── admin_complaint_update.html
│       ├── admin_organization_list.html
│       ├── admin_organization_form.html
│       ├── admin_organization_confirm_delete.html
│       ├── moderator_dashboard.html
│       ├── moderator_complaint_list.html
│       ├── moderator_complaint_detail.html
│       └── moderator_complaint_update.html
└── static/
    └── css/
        └── style.css     # Complete styling
```

## Models (Existing - Not Modified)

### CustomUser
- Fields: username, email, role, tashkilot, phone_number
- Roles: 'user', 'admin', 'moderator'

### Complaint
- Fields: title, description, region, district, location, status, priority, user, masul_tashkilot, answer_text
- Status: 'new', 'in_progress', 'closed', 'rejected'
- Priority: 'low', 'medium', 'high'

### Image
- Fields: complaint (FK), img

### Region, District, Tashkilot
- Location and organization models

## Forms (complaints/forms.py)

### ComplaintCreateForm
- Used by USER to create complaints
- Fields: title, description, region, district, location, priority

### ComplaintAdminUpdateForm
- Used by ADMIN to update complaints
- Fields: status, priority, masul_tashkilot, answer_text

### ComplaintModeratorUpdateForm
- Used by MODERATOR to update complaints
- Fields: status (limited to in_progress/closed), answer_text

### TashkilotForm
- Used by ADMIN to create/update organizations
- Fields: name, manzil, telefon, email, hudud

## Views (complaints/views.py)

### Role-Based Mixins
- **UserRoleMixin**: Ensures user has 'user' role
- **AdminRoleMixin**: Ensures user has 'admin' role
- **ModeratorRoleMixin**: Ensures user has 'moderator' role

### USER Views
1. **UserDashboardView** - Dashboard with statistics
2. **UserComplaintListView** - List of user's own complaints
3. **UserComplaintDetailView** - Detail view of complaint
4. **UserComplaintCreateView** - Create new complaint with image upload
5. **UserComplaintDeleteView** - Delete complaint (only if status='new')
6. **UserProfileView** - User profile page

### ADMIN Views
1. **AdminDashboardView** - Full system statistics
2. **AdminComplaintListView** - All complaints with filters
3. **AdminComplaintDetailView** - Complaint details
4. **AdminComplaintUpdateView** - Update complaint (assign org, change status/priority)
5. **AdminOrganizationListView** - List all organizations
6. **AdminOrganizationCreateView** - Create organization
7. **AdminOrganizationUpdateView** - Update organization
8. **AdminOrganizationDeleteView** - Delete organization

### MODERATOR Views
1. **ModeratorDashboardView** - Dashboard for assigned complaints
2. **ModeratorComplaintListView** - Complaints assigned to moderator's org
3. **ModeratorComplaintDetailView** - Complaint details
4. **ModeratorComplaintUpdateView** - Update status and add response

## URL Routing (complaints/urls.py)

### USER URLs
- `/user/dashboard/` - Dashboard
- `/user/complaints/` - List complaints
- `/user/complaint/<pk>/` - View complaint
- `/user/complaint/create/` - Create complaint
- `/user/complaint/<pk>/delete/` - Delete complaint
- `/user/profile/` - Profile page

### ADMIN URLs
- `/admin/dashboard/` - Dashboard
- `/admin/complaints/` - List all complaints
- `/admin/complaint/<pk>/` - View complaint
- `/admin/complaint/<pk>/update/` - Update complaint
- `/admin/organizations/` - List organizations
- `/admin/organization/create/` - Create organization
- `/admin/organization/<pk>/update/` - Update organization
- `/admin/organization/<pk>/delete/` - Delete organization

### MODERATOR URLs
- `/moderator/dashboard/` - Dashboard
- `/moderator/complaints/` - List assigned complaints
- `/moderator/complaint/<pk>/` - View complaint
- `/moderator/complaint/<pk>/update/` - Update complaint

## Key Features Implemented

### 1. Role-Based Access Control
- Custom mixins enforce role permissions
- Navigation changes based on user role
- Unauthorized access redirects with error message

### 2. Complaint Deletion Rules
- USER can only delete complaints with status='new'
- Once status changes or organization assigned, deletion is blocked
- Delete button disabled in UI for non-deletable complaints

### 3. Status Flow Enforcement
- ADMIN: Can set any status
- MODERATOR: Can only set 'in_progress' or 'closed'
- USER: Cannot change status

### 4. Image Upload
- Multiple images can be uploaded per complaint
- Handled in UserComplaintCreateView
- Images displayed in detail views

### 5. Filtering & Pagination
- Admin complaint list: Filter by status, priority, region
- Moderator complaint list: Filter by status
- Pagination: 10-20 items per page

### 6. Statistics & Dashboards
- USER: Personal statistics (total, closed, in_progress, rejected, success rate)
- ADMIN: System-wide statistics (all statuses, priorities, regions)
- MODERATOR: Organization-specific statistics

### 7. Django Messages
- Success/error feedback on all actions
- Form validation errors displayed
- User-friendly Uzbek messages

## CSS Styling (static/css/style.css)

### Design Theme
- **Primary Color**: Green (#2e7d32) - Eco-friendly theme
- **Clean & Minimal**: Modern card-based layout
- **Responsive**: Mobile-friendly design
- **Consistent**: Unified styling across all pages

### Key Components
- Navigation bar with role-based links
- Statistics cards with icons
- Complaint cards with status badges
- Forms with validation styling
- Tables with hover effects
- Pagination controls
- Alert messages
- Empty states

## Setup Instructions

### 1. Update settings.py
```python
INSTALLED_APPS = [
    # ... existing apps
    'complaints',
    'common',
    'users',
]

TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],
        # ...
    },
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 2. Update main urls.py
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('complaints/', include('complaints.urls')),
    path('users/', include('users.urls')),
    path('', include('common.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3. Update users/views.py login redirect
```python
# In login view, redirect based on role:
if user.role == 'admin':
    return redirect('admin_dashboard')
elif user.role == 'moderator':
    return redirect('moderator_dashboard')
else:  # user
    return redirect('user_dashboard')
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

### 5. Create test users
```python
# Create admin
admin = CustomUser.objects.create_user(
    username='admin',
    password='admin123',
    role='admin'
)

# Create moderator (assign to organization)
moderator = CustomUser.objects.create_user(
    username='moderator',
    password='mod123',
    role='moderator',
    tashkilot=some_organization
)

# Create regular user
user = CustomUser.objects.create_user(
    username='user',
    password='user123',
    role='user'
)
```

## Testing Checklist

### USER Role
- ✅ Can register and login
- ✅ Can create complaints with images
- ✅ Can view only own complaints
- ✅ Can delete complaints only if status='new'
- ✅ Cannot delete after status change
- ✅ Can view profile
- ✅ Dashboard shows correct statistics

### ADMIN Role
- ✅ Can view all complaints
- ✅ Can filter complaints by status/priority/region
- ✅ Can assign organizations to complaints
- ✅ Can change any status
- ✅ Can change priority
- ✅ Can add response text
- ✅ Can create/update/delete organizations
- ✅ Dashboard shows system-wide statistics

### MODERATOR Role
- ✅ Can view only assigned complaints
- ✅ Can change status to in_progress or closed only
- ✅ Can add response text
- ✅ Cannot delete complaints
- ✅ Cannot change priority
- ✅ Dashboard shows organization statistics

### General
- ✅ Navigation changes based on role
- ✅ Unauthorized access is blocked
- ✅ Messages display correctly
- ✅ Forms validate properly
- ✅ Images upload and display
- ✅ Pagination works
- ✅ Responsive design on mobile

## Security Considerations

1. **Role Enforcement**: All views use role mixins
2. **Query Filtering**: Users only see their own data
3. **Permission Checks**: Double-checked in view logic
4. **CSRF Protection**: All forms include {% csrf_token %}
5. **File Upload**: Images validated by Django

## Future Enhancements

1. Add email notifications
2. Add complaint assignment workflow
3. Add comment system
4. Add file attachments (PDFs, documents)
5. Add export to Excel/PDF
6. Add advanced search
7. Add complaint tracking map
8. Add API endpoints for mobile app

## Notes

- All models remain unchanged as requested
- Clean, production-ready code with comments
- Follows Django best practices
- Uses Class-Based Views exclusively
- Uzbek language for user-facing text
- Green eco-friendly theme throughout
- Fully responsive design
- No JavaScript frameworks (pure Django templates)

## Support

For issues or questions, refer to Django documentation:
- Class-Based Views: https://docs.djangoproject.com/en/4.2/topics/class-based-views/
- Forms: https://docs.djangoproject.com/en/4.2/topics/forms/
- Authentication: https://docs.djangoproject.com/en/4.2/topics/auth/
