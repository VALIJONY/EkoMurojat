from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Region, District, Tashkilot


@admin.register(Region)
class RegionAdmin(ModelAdmin):
    """Region Admin with Unfold styling"""
    
    list_display = ['name', 'display_districts_count', 'display_organizations_count']
    search_fields = ['name']
    ordering = ['name']
    
    @display(description="Tumanlar soni", ordering="districts_count")
    def display_districts_count(self, obj):
        count = obj.districts.count()
        return f"{count} ta"
    
    @display(description="Tashkilotlar soni")
    def display_organizations_count(self, obj):
        count = sum(district.tashkilot_set.count() for district in obj.districts.all())
        return f"{count} ta"


@admin.register(District)
class DistrictAdmin(ModelAdmin):
    """District Admin with Unfold styling"""
    
    list_display = ['name', 'display_region', 'display_organizations_count']
    list_filter = ['region']
    search_fields = ['name', 'region__name']
    ordering = ['region__name', 'name']
    
    autocomplete_fields = ['region']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'region')
        }),
    )
    
    @display(description="Viloyat")
    def display_region(self, obj):
        return obj.region.name
    
    @display(description="Tashkilotlar soni")
    def display_organizations_count(self, obj):
        count = obj.tashkilot_set.count()
        return f"{count} ta"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('region')


@admin.register(Tashkilot)
class TashkilotAdmin(ModelAdmin):
    """Tashkilot Admin with Unfold styling"""
    
    list_display = ['name', 'display_location', 'telefon', 'email', 'display_complaints_count']
    list_filter = ['hudud__region', 'hudud']
    search_fields = ['name', 'manzil', 'telefon', 'email']
    ordering = ['name']
    
    autocomplete_fields = ['hudud']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'hudud')
        }),
        ('Aloqa ma\'lumotlari', {
            'fields': ('manzil', 'telefon', 'email')
        }),
    )
    
    @display(description="Joylashuv")
    def display_location(self, obj):
        if obj.hudud:
            return f"{obj.hudud.region.name}, {obj.hudud.name}"
        return "—"
    
    @display(description="Murojaatlar soni", ordering="complaints_count")
    def display_complaints_count(self, obj):
        from complaints.models import Complaint
        count = Complaint.objects.filter(masul_tashkilot=obj).count()
        return f"{count} ta"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('hudud', 'hudud__region')
    
    list_per_page = 25
