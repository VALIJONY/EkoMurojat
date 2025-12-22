from django.shortcuts import render
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views import generic
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from .forms import RegisterForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import random

# Create your views here.

User = get_user_model()

class SignUp(generic.CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('check_code')
    template_name = 'signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data['password'])
        user.is_active = False
        user.save()

        code = str(random.randint(100000, 999999))

        subject = 'Tasdiqlash kodi - EkoMurojaat'
        message = f'Sizning tasdiqlash kodingiz: {code}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(f"Email yuborishda xatolik: {e}")

        self.request.session['verification_code'] = code
        self.request.session['user_id'] = user.id
        
        return super().form_valid(form)

class Check_CodeView(View):
    template_name = 'check_code.html'

    def get(self, request):
        if 'verification_code' not in request.session:
            return redirect('signup')
        return render(request, self.template_name)

    def post(self, request):
        entered_code = request.POST.get('code')
        
        session_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')

        if session_code and entered_code == session_code and user_id:
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                
                del request.session['verification_code']
                del request.session['user_id']
                
                return redirect('login') 
            except User.DoesNotExist:
                return render(request, self.template_name, {'error': "Foydalanuvchi topilmadi."})
        else:
            return render(request, self.template_name, {'error': "Kod noto'g'ri kiritildi!"})


class LoginView(View):
    template_name = 'login.html'
    def get(self,request):
        return render(request,self.template_name) 
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            if hasattr(user, 'role'):
                if user.role == 'admin':
                    return redirect('dashboard_admin')
                elif user.role == 'moderator':
                    return redirect('dashboard_moderator')
                else:  
                    return redirect('user_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            return render(request, self.template_name, {'error': 'Login yoki parol xato'})
        
class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('login')