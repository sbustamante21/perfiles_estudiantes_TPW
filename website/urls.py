from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.main_page, name="main_page"),
    path("student_register/", views.student_register, name="student_register"),
    path("professor_register/", views.professor_register, name="professor_register"),
    path("login/", views.do_login, name="login"),
    path("main_page/", views.main_page, name="main_page"),
    path("welcome/", views.welcome, name="welcome"),
    path("register/", views.register, name="register"),
    path("logout/", views.do_logout, name="logout"),
    path("delete_user/", views.delete_user, name="delete_user"),
    path("admin_page/<str:modelo>/", views.admin_page, name="admin_page"),
    path("profile_page/<str:id_user>", views.profile_page, name="profile_page"),
    path("about_us/", views.about_us, name="about_us"),
    path("generate_pdf/<str:id_user>/", views.generate_pdf, name="generate_pdf"),
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("professor_edit/", views.professor_edit, name="professor_edit"),
    path("student_edit/", views.student_edit, name="student_edit"),
    path("change_password/", views.change_password, name="change_password"),
    path("send_email/", views.send_custom_email, name="send_custom_email"),
    path("load_cplans/", views.load_cplans, name="load_cplans")
]
