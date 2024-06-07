from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('student_register/', views.student_register, name='student_register'),
    path('professor_register/', views.professor_register, name='professor_register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('home/', views.home, name='home'),
    path('inicio/',  views.inicio, name="inicio"),
    path('register/', views.register, name='register'),
]
