import json
from django.shortcuts import render
from django.views import View
from django.db.models import Count
from .models import Region, District
from complaints.models import Complaint

# Create your views here.
class DashboardView(View):
    def get(self, request):
        return render(request, 'dashboard.html')

def home_view(request):
    # 1. Filtrlash logikasi
    complaints = Complaint.objects.all().order_by('-created_at')
    
    region_id = request.GET.get('region')
    district_id = request.GET.get('district')

    if region_id:
        complaints = complaints.filter(region_id=region_id)
    if district_id:
        complaints = complaints.filter(district_id=district_id)

    # 2. Xarita uchun ma'lumotlarni tayyorlash
    # Faqat lokatsiyasi bor murojaatlarni olamiz
    map_data = []
    for c in complaints:
        if c.location:
            map_data.append({
                'id': c.id,
                'title': c.title,
                'lat': c.location.y, # Latitude
                'lng': c.location.x, # Longitude
                'priority': c.priority, # Rang uchun kerak (high, medium, low)
                'status': c.get_status_display(),
                'region': c.region.name if c.region else '',
                'district': c.district.name if c.district else ''
            })

    # 3. Top 10 (Yuqori prioritetli)
    high_priority_complaints = Complaint.objects.filter(
        priority='high',
        status__in=['new', 'in_progress'],
    ).order_by('-created_at')[:10]

    regions = Region.objects.all()
    districts = District.objects.all()

    context = {
        'complaints_count': complaints.count(),
        'map_data': json.dumps(map_data), # Xarita uchun JSON
        'top_complaints': high_priority_complaints,
        'regions': regions,
        'districts': districts,
        'selected_region': int(region_id) if region_id else None,
        'selected_district': int(district_id) if district_id else None,
        'districts_json': json.dumps([
            {'id': d.id, 'name': d.name, 'region_id': d.region_id} 
            for d in districts
        ])  
    }

    return render(request, 'home.html', context)