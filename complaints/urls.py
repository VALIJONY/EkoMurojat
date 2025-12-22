from django.urls import path
from . import views

urlpatterns = [
    # ============================================================================
    # USER URLS
    # ============================================================================
    path('user/dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('user/complaints/', views.UserComplaintListView.as_view(), name='user_complaints'),
    path('user/complaint/<int:pk>/', views.UserComplaintDetailView.as_view(), name='user_complaint_detail'),
    path('user/complaint/create/', views.UserComplaintCreateView.as_view(), name='user_complaint_create'),
    path('user/complaint/<int:pk>/delete/', views.UserComplaintDeleteView.as_view(), name='user_complaint_delete'),
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # ============================================================================
    # ADMIN URLS (Custom - not Django admin)
    # ============================================================================
    path('dashboard/management/', views.AdminDashboardView.as_view(), name='dashboard_admin'),
    path('dashboard/management/complaints/', views.AdminComplaintListView.as_view(), name='complaints_admin'),
    path('dashboard/management/complaint/<int:pk>/', views.AdminComplaintDetailView.as_view(), name='complaint_detail_admin'),
    path('dashboard/management/complaint/<int:pk>/update/', views.AdminComplaintUpdateView.as_view(), name='complaint_update_admin'),
    
    # Organization management
    path('dashboard/management/organizations/', views.AdminOrganizationListView.as_view(), name='organizations_admin'),
    path('dashboard/management/organization/create/', views.AdminOrganizationCreateView.as_view(), name='organization_create_admin'),
    path('dashboard/management/organization/<int:pk>/update/', views.AdminOrganizationUpdateView.as_view(), name='organization_update_admin'),
    path('dashboard/management/organization/<int:pk>/delete/', views.AdminOrganizationDeleteView.as_view(), name='organization_delete_admin'),
    
    # Priority management
    path('dashboard/management/priority/', views.AdminPriorityManagementView.as_view(), name='admin_priority_management'),
    
    # User management
    path('dashboard/management/users/', views.AdminUserListView.as_view(), name='users_admin'),
    path('dashboard/management/user/create/', views.AdminUserCreateView.as_view(), name='user_create_admin'),
    path('dashboard/management/user/<int:pk>/update/', views.AdminUserUpdateView.as_view(), name='user_update_admin'),
    path('dashboard/management/user/<int:pk>/delete/', views.AdminUserDeleteView.as_view(), name='user_delete_admin'),
    
    # ============================================================================
    # MODERATOR URLS
    # ============================================================================
    path('moderator/dashboard/', views.ModeratorDashboardView.as_view(), name='dashboard_moderator'),
    path('moderator/complaints/', views.ModeratorComplaintListView.as_view(), name='complaints_moderator'),
    path('moderator/complaint/<int:pk>/', views.ModeratorComplaintDetailView.as_view(), name='complaint_detail_moderator'),
    path('moderator/complaint/<int:pk>/update/', views.ModeratorComplaintUpdateView.as_view(), name='complaint_update_moderator'),
]
