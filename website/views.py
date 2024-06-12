from django.shortcuts import render, redirect, reverse
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from .forms import StudentRegisterForm, UserRegisterForm, ProfileRegisterForm
from .models import Student, Role, Profile, CurriculumPlan, Degree
from django.contrib.auth.views import LogoutView

# Create your views here.


# Views
@login_required
def main_page(request):
    return render(request, "website/main_page.html", {})


def do_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect(
                    reverse("main_page")
                )  # aca condicionar segun el rol de usuario
            else:
                messages.info(request, "Invalid credentials")
                return redirect(reverse("login"))
        else:
            messages.error(request, "Error processing your request")
            return render(request, "website/login.html", {"form": form})
    else:
        form = AuthenticationForm()
        return render(request, "website/login.html", {"form": form})


def do_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("welcome")

def delete_user(request):
    user = request.user
    detete_user = False
    if user.role == user.DOCENTE:
        if not user.receiver.exists() and not user.sender.exists() and delete_user:
            delete_user = True
        else: 
            user.is_active = False
            user.save()
    return redirect("welcome")
    
class CustomLoginView(auth_views.LoginView):
    template_name = "website/login.html"


def welcome(request):
    return render(request, "website/welcome.html")


def register(request):
    return render(request, "website/register.html")


def student_register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileRegisterForm(request.POST)
        student_form = StudentRegisterForm(request.POST, request.FILES)

        email = request.POST.get("email")

        if user_form.is_valid() and profile_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password1"])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            default_role = Role.objects.get(name="ESTUDIANTE")
            profile.role_id = default_role
            profile.save()

            student = student_form.save(commit=False)
            student.user_id = profile
            student.save()

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

        email = request.POST.get("email")

        if not email.endswith("@utalca.cl"):
            user_form.add_error("email", "You must use your institution's email.")
            return render(
                request,
                "website/professor_register.html",
                {
                    "user_form": user_form,
                    "profile_form": profile_form,
                },
            )

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
