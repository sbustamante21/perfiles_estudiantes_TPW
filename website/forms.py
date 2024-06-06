from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Student, CurriculumPlan, Degree

from django.utils.translation import gettext_lazy as _

class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        labels = {
            'username': _('Nombre de usuario'),
            'email': _('Correo Institucional'),
            'password': _('Contraseña'),
            'first_name': _('Nombre'),
            'last_name':_('Apellido'),
        }
    
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
    class Meta:
        model = Student
        fields = ['admission_year', 'personal_mail', 'phone_number', 'pfp', 'degree_id', 'curriculum_plan_id',]
        exclude = ["pfp"]
        labels = {
            'admission_year': _('Año de admisión'),
            'personal_mail': _('Correo personal'),
            'phone_number': _('Número de teléfono'),
            'pfp': _('Foto de perfil'),
            'curriculum_plan_id': _('Plan de estudios'),
            'degree_id': _('Título'),
        }

    admission_year = forms.IntegerField(required=True)
    personal_mail = forms.EmailField(required=False)
    phone_number = forms.IntegerField(required=False)
    curriculum_plan_id = forms.ModelChoiceField(queryset=CurriculumPlan.objects.all(), required=True)
    degree_id = forms.ModelChoiceField(queryset=Degree.objects.all(), required=True)
