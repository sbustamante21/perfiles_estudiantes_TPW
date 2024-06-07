from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Student, CurriculumPlan, Degree
from django.core.validators import MaxValueValidator
import datetime

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name','password1', 'password2',]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This value already exists.')
        if not email.endswith("@alumnos.utalca.cl") and not email.endswith("@utalca.cl"):
            raise forms.ValidationError("You must use your institution's e-mail.")
        return email


class ProfileRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["role_id", "user"]

class StudentRegisterForm(forms.ModelForm):
    admission_year = forms.IntegerField(required=True)
    personal_mail = forms.EmailField(required=False)
    phone_number = forms.IntegerField(required=False)
    curriculum_plan_id = forms.ModelChoiceField(queryset=CurriculumPlan.objects.all(), required=True)
    degree_id = forms.ModelChoiceField(queryset=Degree.objects.all(), required=True)

    class Meta:
        model = Student
        fields = ['admission_year', 'personal_mail', 'phone_number', 'pfp', 'degree_id', 'curriculum_plan_id',]
        exclude = ["pfp"]

    def clean_admission_year(self):
        admission_year = self.cleaned_data.get('admission_year')

        if not datetime.datetime.now().year >= admission_year >= 1980:
            raise forms.ValidationError('Year out of bounds')
        return admission_year
    
    def clean_personal_mail(self):
        email = self.cleaned_data.get('personal_mail')

        if email != "":
            if Student.objects.filter(personal_mail=email).exists():
                raise forms.ValidationError('This email is already used')
        return email
    
    def clean_phone_number(self):
        number = self.cleaned_data.get('phone_number')

        if number != "":
            if Student.objects.filter(phone_number=number).exists():
                raise forms.ValidationError('This phone number is already used')
            elif len(str(num)) != 9:
                raise forms.ValidationError('The phone number must be 9 digits long')
        return email
