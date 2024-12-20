from django.urls import path, include
from django.views.generic.base import TemplateView
from accounts.views import SignUpView, ProfileView


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('welcome/', TemplateView.as_view(template_name='registration/welcome.html'), name='welcome'),
    path("", include("django.contrib.auth.urls")), 
]
