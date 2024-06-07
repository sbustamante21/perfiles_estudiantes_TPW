from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from .forms import StudentRegisterForm, UserRegisterForm, ProfileRegisterForm
from .models import Student, Role, Profile, CurriculumPlan
from django.contrib.auth.views import LogoutView

# Create your views here.


# Views
@login_required
def home(request):
    return render(request, "website/success.html", {})


def do_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("inicio")


class CustomLoginView(auth_views.LoginView):
    template_name = "website/login.html"


def inicio(request):
    return render(request, "website/inicio.html")


def login(request):
    return render(request, "website/login.html")


def register(request):
    return render(request, "website/register.html")


def student_register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileRegisterForm(request.POST)
        student_form = StudentRegisterForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password1"])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            default_role = Role.objects.get(
                name="ESTUDIANTE"
            )  # Change 'Student' to the appropriate role name
            profile.role_id = default_role
            profile.save()

            student = student_form.save(commit=False)
            student.user_id = profile
            student.save()

            # Redirect to the login page
            return redirect(reverse("inicio"))

    else:
        user_form = UserRegisterForm()
        profile_form = ProfileRegisterForm()
        student_form = StudentRegisterForm()

    return render(
        request,
        "website/student_register.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "student_form": student_form,
        },
    )


def professor_register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileRegisterForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password1"])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            professor_role = Role.objects.get(name="DOCENTE")
            profile.role_id = professor_role
            profile.save()

            return redirect(reverse("inicio"))
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileRegisterForm()

    return render(
        request,
        "website/professor_register.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )


def login(request):
    return render(request, "website/login.html")
