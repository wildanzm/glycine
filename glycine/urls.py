"""
URL configuration for glycine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from django.views.generic.base import RedirectView
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard', core_views.dashboard, name='dashboard'),
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=True)),
    path('pompa-air', core_views.water_pump, name='water-pump'),
    path('devices', core_views.device, name='device'),
]
