from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Student, CurriculumPlan, Degree, User, PeriodType, InterestType
from django.core.validators import MaxValueValidator
import datetime

class AuthenticationFormWithInactiveUsersOkay(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("Cuenta inactiva. Por favor, comuníquese con los administradores: sbustamante21@alumnos.utalca.cl, mlolas19@alumnos.utalca.cl, cecastillo19@alumnos.utalca.cl")

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This value already exists.")
        return email

class UserRegisterFormAdmin(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    is_active = forms.BooleanField(required=False, initial=True, label="Activo")
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Rol")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "role"
        ]

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super(UserRegisterFormAdmin, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists() and self.instance.email != email:
            raise forms.ValidationError("This value already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class StudentRegisterForm(forms.ModelForm):
    admission_year = forms.IntegerField(required=True)
    personal_mail = forms.EmailField(required=False)
    phone_number = forms.IntegerField(required=False)
    curriculum_plan_id = forms.ModelChoiceField(
        queryset=CurriculumPlan.objects.all(), required=True
    )
    degree_id = forms.ModelChoiceField(queryset=Degree.objects.all(), required=True)

    class Meta:
        model = Student
        fields = [
            "admission_year",
            "personal_mail",
            "phone_number",
            "pfp",
            "degree_id",
            "curriculum_plan_id",
        ]
        exclude = ["pfp"]

    def clean_admission_year(self):
        admission_year = self.cleaned_data.get("admission_year")

        if not datetime.datetime.now().year >= admission_year >= 1980:
            raise forms.ValidationError("Year out of bounds")
        return admission_year

    def clean_personal_mail(self):
        email = self.cleaned_data.get("personal_mail")

        if email != "":
            if Student.objects.filter(personal_mail=email).exists():
                raise forms.ValidationError("This email is already used")
        return email

    def clean_phone_number(self):
        number = self.cleaned_data.get("phone_number")

        if number is not None:
            if Student.objects.filter(phone_number=number).exists():
                raise forms.ValidationError("This phone number is already used")
            elif len(str(number)) != 9:
                raise forms.ValidationError("The phone number must be 9 digits long")
        return number

class PeriodTypeFormAdmin(forms.ModelForm):
    name = forms.CharField(required=True)

    class Meta:
        model = PeriodType
        fields = [
            "name",
        ]   

class CurriculumPlanFormAdmin(forms.ModelForm):
    name = forms.CharField(required=True)
    impl_year = forms.IntegerField()
    degree_id = forms.ModelChoiceField(queryset=Degree.objects.all(), required=True)

    class Meta:
        model = CurriculumPlan
        fields = [
            "name",
            "impl_year",
            "degree_id",
        ]   

class InterestTypeFormAdmin(forms.ModelForm):
    name = forms.CharField(required=True)
    
    class Meta:
        model = InterestType
        fields = [
            "name",
        ]
        
class DegreeFormAdmin(forms.ModelForm):
    name = forms.CharField(required=True)
    
    class Meta:
        model = Degree
        fields = [
            "name",
        ]
        
class StudentRegisterFormAdmin(forms.ModelForm):
    admission_year = forms.IntegerField(required=True)
    personal_mail = forms.EmailField(required=False)
    phone_number = forms.IntegerField(required=False)
    curriculum_plan_id = forms.ModelChoiceField(
        queryset=CurriculumPlan.objects.all(), required=True
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), required=True
    )
    degree_id = forms.ModelChoiceField(queryset=Degree.objects.all(), required=True)
    pfp = forms.ImageField(required=False)

    class Meta:
        model = Student
        fields = [
            "admission_year",
            "personal_mail",
            "phone_number",
            "pfp",
            "degree_id",
            "curriculum_plan_id",
            "user",
        ]
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super(StudentRegisterFormAdmin, self).__init__(*args, **kwargs)

    def clean_admission_year(self):
        admission_year = self.cleaned_data.get("admission_year")

        if not datetime.datetime.now().year >= admission_year >= 1980:
            raise forms.ValidationError("Year out of bounds")
        return admission_year

    def clean_personal_mail(self):
        email = self.cleaned_data.get("personal_mail")

        if email != "":
            if Student.objects.filter(personal_mail=email).exists() and self.instance.personal_mail != email:
                raise forms.ValidationError("This email is already used")
        return email

    def clean_phone_number(self):
        number = self.cleaned_data.get("phone_number")

        if number is not None:
            if Student.objects.filter(phone_number=number).exists() and self.instance.number != number:
                raise forms.ValidationError("This phone number is already used")
            elif len(str(number)) != 9:
                raise forms.ValidationError("The phone number must be 9 digits long")
        return number
