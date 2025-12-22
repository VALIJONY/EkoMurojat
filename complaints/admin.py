from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from django.utils.html import format_html
from .models import Complaint, Image


class ImageInline(TabularInline):
    """Inline admin for complaint images"""
    model = Image
    extra = 1
    fields = ['img', 'image_preview']
    readonly_fields = ['image_preview']
    
    @display(description="Rasm ko'rinishi")
    def image_preview(self, obj):
        if obj.img:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 8px;" />', obj.img.url)
        return "—"


@admin.register(Complaint)
class ComplaintAdmin(ModelAdmin):
    """Complaint Admin with Unfold styling"""
    
    list_display = ['title', 'display_user', 'display_region', 'display_status', 'display_priority', 'display_organization', 'created_at']
    list_filter = ['status', 'priority', 'region', 'district', 'masul_tashkilot', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'user__email']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    inlines = [ImageInline]
    
    fieldsets = (
        ('Murojaat ma\'lumotlari', {
            'fields': ('title', 'description', 'user')
        }),
        ('Joylashuv', {
            'fields': ('region', 'district', 'location')
        }),
        ('Holat va prioritet', {
            'fields': ('status', 'priority', 'masul_tashkilot')
        }),
        ('Javob', {
            'fields': ('answer_text',),
            'classes': ['collapse']
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at', 'viewed_at', 'closed_at'),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'viewed_at', 'closed_at']
    
    autocomplete_fields = ['user', 'masul_tashkilot']
    
    @display(description="Foydalanuvchi")
    def display_user(self, obj):
        return f"{obj.user.username} ({obj.user.get_role_display()})"
    
    @display(description="Hudud")
    def display_region(self, obj):
        if obj.district:
            return f"{obj.region.name}, {obj.district.name}"
        return obj.region.name if obj.region else "—"
    
    @display(description="Holat", label=True)
    def display_status(self, obj):
        status_colors = {
            'new': 'info',
            'in_progress': 'warning',
            'closed': 'success',
            'rejected': 'danger',
        }
        return obj.get_status_display(), status_colors.get(obj.status, 'info')
    
    @display(description="Prioritet", label=True)
    def display_priority(self, obj):
        if not obj.priority:
            return "Belgilanmagan", "secondary"
        
        priority_colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
        }
        return obj.get_priority_display(), priority_colors.get(obj.priority, 'info')
    
    @display(description="Mas'ul tashkilot")
    def display_organization(self, obj):
        return obj.masul_tashkilot.name if obj.masul_tashkilot else "Belgilanmagan"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'region', 'district', 'masul_tashkilot')
    
    list_per_page = 25


@admin.register(Image)
class ImageAdmin(ModelAdmin):
    """Image Admin with Unfold styling"""
    
    list_display = ['id', 'display_complaint', 'image_preview', 'created_date']
    list_filter = ['complaint__status', 'complaint__created_at']
    search_fields = ['complaint__title', 'complaint__user__username']
    ordering = ['-id']
    
    fields = ['complaint', 'img', 'image_preview']
    readonly_fields = ['image_preview', 'created_date']
    
    @display(description="Murojaat")
    def display_complaint(self, obj):
        return obj.complaint.title
    
    @display(description="Rasm")
    def image_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.img.url
            )
        return "—"
    
    @display(description="Yuklangan sana")
    def created_date(self, obj):
        return obj.complaint.created_at.strftime("%d.%m.%Y %H:%M")
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('complaint', 'complaint__user')
