from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Student, CurriculumPlan, Degree

class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

class ProfileRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["role_id", "user"]

class StudentRegisterForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['admission_year', 'personal_mail', 'phone_number', 'pfp', 'curriculum_plan_id', 'degree_id']
        exclude = ["pfp"]

    admission_year = forms.IntegerField(required=True)
    personal_mail = forms.EmailField(required=False)
    phone_number = forms.IntegerField(required=False)
    curriculum_plan_id = forms.ModelChoiceField(queryset=CurriculumPlan.objects.all(), required=True)
    degree_id = forms.ModelChoiceField(queryset=Degree.objects.all(), required=True)
