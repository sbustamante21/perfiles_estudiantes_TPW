from django.urls import path
from . import views

urlpatterns = [
    path('student_register/', views.student_register, name='student_register'),
    path('professor_register/', views.professor_register, name='professor_register'),
    path('login/', views.login, name='login')
]

