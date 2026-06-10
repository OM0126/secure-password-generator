"""
URL configuration for secure_password_generator project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('password_generator.urls')),
]
