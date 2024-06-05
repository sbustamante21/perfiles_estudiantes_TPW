from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import StudentRegisterForm, UserRegisterForm, ProfileRegisterForm
from .models import Student, Role, Profile


# Create your views here.

def student_register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileRegisterForm(request.POST)
        student_form = StudentRegisterForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user

            # Set the role_id value (assumes you have a default Role object you want to use)
            default_role = Role.objects.get(name='ESTUDIANTE')  # Change 'Student' to the appropriate role name
            profile.role_id = default_role
            profile.save()
            
            student = student_form.save(commit=False)
            student.user_id = profile
            student.save()
            
            # Redirect to the login page
            return redirect('')

            # Authenticate and log the user in
            # new_user = authenticate(username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'])
            # login(request, new_user)
            
            # return redirect('home')
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileRegisterForm()
        student_form = StudentRegisterForm()
        
    return render(request, 'website/student_register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'student_form': student_form
    })

def professor_register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileRegisterForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            professor_role = Role.objects.get(name='DOCENTE')
            profile.role_id = professor_role
            profile.save()
            
            return redirect(reverse(''))
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileRegisterForm()
        
    return render(request, 'website/professor_register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
