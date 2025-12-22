from django import forms
from django.contrib.auth.models import User
from .models import Complaint, Image
from common.models import Region, District, Tashkilot
from users.models import CustomUser


class ComplaintCreateForm(forms.ModelForm):
    """
    Form for USER to create a new complaint
    """
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'region', 'district', 'location']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Murojaat sarlavhasi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Muammoni batafsil tavsiflang...',
                'rows': 5
            }),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'district': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manzilni xaritadan belgilang',
                'readonly': 'readonly',
            }),
        }


class ComplaintAdminUpdateForm(forms.ModelForm):
    """
    Form for ADMIN to update complaint (assign organization, change priority, change status)
    """
    class Meta:
        model = Complaint
        fields = ['status', 'priority', 'masul_tashkilot', 'answer_text']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'masul_tashkilot': forms.Select(attrs={'class': 'form-control'}),
            'answer_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Javob matni...'
            }),
        }


class ComplaintModeratorUpdateForm(forms.ModelForm):
    """
    Form for MODERATOR to update complaint (change status to in_progress/solved, add response)
    """
    class Meta:
        model = Complaint
        fields = ['status', 'answer_text']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'answer_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Javob matni...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Moderator can only set status to in_progress or closed
        self.fields['status'].choices = [
            ('in_progress', 'Jarayonda'),
            ('closed', 'Yopilgan'),
        ]


class ImageUploadForm(forms.ModelForm):
    """
    Form for uploading complaint images
    """
    class Meta:
        model = Image
        fields = ['img']
        widgets = {
            'img': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }


class TashkilotForm(forms.ModelForm):
    """
    Form for ADMIN to create/update organizations
    """
    class Meta:
        model = Tashkilot
        fields = ['name', 'manzil', 'telefon', 'email', 'hudud']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tashkilot nomi'
            }),
            'manzil': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manzil'
            }),
            'telefon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 XX XXX XX XX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'hudud': forms.Select(attrs={'class': 'form-control'}),
        }


class UserCreateForm(forms.ModelForm):
    """
    Form for ADMIN to create users for organizations
    """
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Parol'
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Parolni tasdiqlang'
    }))
    organization = forms.ModelChoiceField(
        queryset=Tashkilot.objects.all(),
        empty_label="Tashkilotni tanlang",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='user'
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'role', 'organization']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ism'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Familiya'
            }),
        }
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Parollar mos kelmadi!")
        return password_confirm
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
