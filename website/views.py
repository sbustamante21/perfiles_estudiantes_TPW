from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

# Views
@login_required
def home(request):
    return render(request, "website/success.html", {})

class CustomLoginView(auth_views.LoginView):
    template_name = 'website/login.html'

# Create your views here.
def inicio(request):
    return render(request, 'website/inicio.html')

def login(request):
    return render(request, 'website/login.html')

def register(request):
    return render(request, 'website/register.html')
