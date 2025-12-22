from django import forms

from .models import CustomUser




class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
    
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Parollar mos kelmadi")

        return cleaned_data

    def hesh_password(self):
        password =clean(self)
        self.save()
        
