"""
URL configuration for elearner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500, handler403, handler400
from django.conf.urls.static import static
from courses.views import HomeView, TemplateView
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")), 
    path("courses/", include("courses.urls")), 
    path('', HomeView.as_view(), name='home'),
    path('policy', TemplateView.as_view(template_name='policy.html'), name='policy'),
    path('faq', TemplateView.as_view(template_name='faq.html'), name='faq'),
    path('about', TemplateView.as_view(template_name='about.html'), name='about'),
]

handler400 = TemplateView.as_view(template_name="errors/400.html")
handler403 = TemplateView.as_view(template_name="errors/403.html")
handler404 = TemplateView.as_view(template_name="errors/404.html")
handler500 = TemplateView.as_view(template_name="errors/500.html")

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)