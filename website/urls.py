from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("student_register/", views.student_register, name="student_register"),
    path("professor_register/", views.professor_register, name="professor_register"),
    path("login/", views.do_login, name="login"),
    path("main_page/", views.main_page, name="main_page"),
    path("welcome/", views.welcome, name="welcome"),
    path("register/", views.register, name="register"),
    path("logout/", views.do_logout, name="logout"),
    path("delete_user/", views.delete_user, name="delete_user"),
    path("admin_page/<str:modelo>/", views.admin_page, name="admin_page"),
    path("profile_page/", views.profile_page, name="profile_page"),
    path("professor_edit/", views.professor_edit, name="professor_edit"),
    path("student_edit/", views.student_edit, name="student_edit"),
]
