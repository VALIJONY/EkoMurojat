from django.contrib.gis.db import models

# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=255, verbose_name="Viloyat nomi")

    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"

# 2. DISTRICTS
class District(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tuman nomi")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts', verbose_name="Viloyat")
    
    # Agar kelajakda "Lokatsiya qaysi tumanga tushishini" avtomat aniqlash kerak bo'lsa,
    # bu yerga PolygonField qo'shish kerak bo'ladi.
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"

# 3. TASHKILOTLAR
class Tashkilot(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tashkilot nomi")
    manzil = models.CharField(max_length=255, verbose_name="Manzil")
    telefon = models.CharField(max_length=50, verbose_name="Telefon")
    email = models.EmailField(verbose_name="Email")
    hudud = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, verbose_name="Hudud (Tuman)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tashkilot"
        verbose_name_plural = "Tashkilotlar"