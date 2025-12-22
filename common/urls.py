from django.urls import path
from django.views.generic import RedirectView
from .views import home_view

urlpatterns = [
    path("", RedirectView.as_view(url="home/", permanent=True)),
    path('home/', home_view, name='home'),
]
