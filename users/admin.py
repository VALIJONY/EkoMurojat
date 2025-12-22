from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    """Custom User Admin with Unfold styling"""
    
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = ['username', 'email', 'display_role', 'display_tashkilot', 'phone_number', 'display_status', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'tashkilot', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('username', 'password')
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'user_image')
        }),
        ('Rol va tashkilot', {
            'fields': ('role', 'tashkilot')
        }),
        ('Ruxsatlar', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ['collapse']
        }),
        ('Muhim sanalar', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    add_fieldsets = (
        ('Yangi foydalanuvchi yaratish', {
            'classes': ['wide'],
            'fields': ('username', 'password1', 'password2', 'email', 'role', 'tashkilot', 'phone_number'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    @display(description="Rol", label=True)
    def display_role(self, obj):
        role_colors = {
            'admin': 'danger',
            'moderator': 'warning',
            'user': 'success',
        }
        return obj.get_role_display(), role_colors.get(obj.role, 'info')
    
    @display(description="Tashkilot")
    def display_tashkilot(self, obj):
        return obj.tashkilot.name if obj.tashkilot else "—"
    
    @display(description="Holat", label=True)
    def display_status(self, obj):
        if obj.is_active:
            return "Faol", "success"
        return "Nofaol", "danger"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('tashkilot')
