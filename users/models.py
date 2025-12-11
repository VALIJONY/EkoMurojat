from django.db import models
from django.contrib.auth.models import AbstractUser

from common.models import Tashkilot 


# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'Foydalanuvchi'),
        ('moderator', 'Moderator'),
    )
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user', verbose_name="Rol")
    tashkilot = models.ForeignKey(Tashkilot, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tashkilot")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqam")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"