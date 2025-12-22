from django.urls import path
from .views import SignUp, LoginView,LogoutView, Check_CodeView

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('check-code/', Check_CodeView.as_view(), name='check_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
