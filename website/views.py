from django.shortcuts import render, redirect, reverse
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from .forms import StudentRegisterForm, UserRegisterForm
from .models import Student, Role, CurriculumPlan, Degree, User
from django.contrib.auth.views import LogoutView

# Create your views here.


# Views
@login_required
def main_page(request):
    return render(request, "website/main_page.html", {})

@login_required
def admin_page(request):
    return render(request, "website/admin_page.html")

def do_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                if user.role == "0":
                    return redirect(
                        reverse("admin_page")
                    )
                else:
                    return redirect(
                        reverse("main_page")
                    )
            else:
                messages.info(request, "Invalid credentials")
                return redirect(reverse("login"))
        else:
            messages.error(request, "Error processing your request")
            return render(request, "website/login.html", {"form": form})
    else:
        form = AuthenticationForm()
        return render(request, "website/login.html", {"form": form})

@login_required
def profile_page(request):
    user = request.user
    if user.role == user.STUDENT:
        degree = user.student.degree_id
        adm_year = user.student.admission_year
        pfp = user.student.pfp
        context = {"user": user, "role": "Estudiante", "degree":degree, "year":adm_year, "pfp":pfp}
    elif user.role == user.PROFESSOR:
        context = {"user":user, "role":"Docente"}

    return render(request, "website/profile_page.html", context)


def do_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("welcome")


def welcome(request):
    return render(request, "website/welcome.html")


def register(request):
    return render(request, "website/register.html")

def student_register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        student_form = StudentRegisterForm(request.POST, request.FILES)

        email = request.POST.get("email")

        if not email.endswith("@alumnos.utalca.cl"):
            user_form.add_error("email", "You must use your institution's email.")
            return render(
                request,
                "website/student_register.html",
                {
                    "user_form": user_form,
                    "student_form": student_form,
                },
            )

        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password1"])
            user.role = User.STUDENT
            user.save()

            student = student_form.save(commit=False)
            student.user = user
            student.save()

            return redirect(reverse("welcome"))

    else:
        user_form = UserRegisterForm()
        student_form = StudentRegisterForm()

    return render(
        request,
        "website/student_register.html",
        {
            "user_form": user_form,
            "student_form": student_form,
        },
    )


def professor_register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)

        email = request.POST.get("email")

        if not email.endswith("@utalca.cl"):
            user_form.add_error("email", "You must use your institution's email.")
            return render(
                request,
                "website/professor_register.html",
                {
                    "user_form": user_form,
                },
            )

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password1"])
            user.role = User.PROFESSOR
            user.save()

            return redirect(reverse("welcome"))
    else:
        user_form = UserRegisterForm()

    return render(
        request,
        "website/professor_register.html",
        {
            "user_form": user_form,
        },
    )
