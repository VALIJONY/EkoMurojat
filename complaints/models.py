from django.contrib.gis.db import models

from django.conf import settings # User modelni olishning to'g'ri yo'li
from common.models import Region, District, Tashkilot


# Create your models here.
# 5. COMPLAINTS (Asosiy o'zgarish shu yerda)
class Complaint(models.Model):
    STATUS_CHOICES = (
        ('new', 'Yangi'),
        ('in_progress', 'Jarayonda'),
        ('closed', 'Yopilgan'),
        ('rejected', 'Rad etilgan'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Past'),
        ('medium', 'O\'rta'),
        ('high', 'Yuqori'),
    )

    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif")
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, verbose_name="Viloyat")
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, verbose_name="Tuman")
    
    # --- POINTFIELD ---
    # srid=4326 bu GPS koordinatalari (WGS 84) standarti
    location = models.PointField(srid=4326, blank=True, null=True, verbose_name="Lokatsiya")
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new', verbose_name="Holat")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='complaints', verbose_name="Foydalanuvchi")
    masul_tashkilot = models.ForeignKey(Tashkilot, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mas'ul tashkilot")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Muhimlik")
    answer_text = models.TextField(blank=True, null=True, verbose_name="Javob matni")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"

# 6. IMAGES
class Image(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to='complaint_images/')

    def __str__(self):
        return f"Image {self.id}"