from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    Student,
    CurriculumPlan,
    Degree,
    User,
    PeriodType,
    InterestType,
    History,
    Subject,
    Interest,
)
from django.core.validators import MaxValueValidator
import datetime


class AuthenticationFormWithInactiveUsersOkay(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "Cuenta inactiva. Por favor, comuníquese con los administradores: sbustamante21@alumnos.utalca.cl, mlolas19@alumnos.utalca.cl, cecastillo19@alumnos.utalca.cl"
            )


class StudentHistory(forms.ModelForm):
    NUMBER_CHOICES = [
        (1, "1"),
        (2, "2"),
    ]
    subject_id = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True)
    interest_type_id = forms.ModelChoiceField(
        queryset=InterestType.objects.exclude(name="AUXILIO"), required=True
    )
    year = forms.IntegerField(required=True)
    period = forms.ChoiceField(choices=NUMBER_CHOICES, required=True)
    student_id = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        disabled=True,
        widget=forms.Select(attrs={"class": "hidden"}),
    )

    class Meta:
        model = History
        fields = [
            "subject_id",
            "interest_type_id",
            "year",
            "period",
            "student_id",
        ]

    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop("student_id", None)
        super(StudentHistory, self).__init__(*args, **kwargs)
        if student_id:
            self.fields["student_id"].initial = student_id

    def clean_year(self):
        year = self.cleaned_data.get("year")

        if not datetime.datetime.now().year >= year >= 1980:
            raise forms.ValidationError("Year out of bounds")
        return year


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
    password = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "role",
        ]

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance", None)
        super(UserRegisterFormAdmin, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists() and self.instance.email != email:
            raise forms.ValidationError("This value already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password"]
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
    impl_year = forms.IntegerField(required=True)
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
        
class SubjectFormAdmin(forms.ModelForm):
    NUMBER_CHOICES = [
        (1, "1"),
        (2, "2"),
    ]
    name = forms.CharField(required=True)
    period = forms.ChoiceField(choices=NUMBER_CHOICES, required=True)
    period_type = forms.ModelChoiceField(queryset=PeriodType.objects.all(),required=True)
    plan_id = forms.ModelChoiceField(queryset=CurriculumPlan.objects.all(), required=True)
    
    class Meta:
        model = Subject
        fields = [
            "name",
            "period",
            "period_type",
            "plan_id",
        ]

class InterestFormAdmin(forms.ModelForm):
    interest_type_id = forms.ModelChoiceField(queryset=InterestType.objects.all(), required=True)
    student_id = forms.ModelChoiceField(queryset=Student.objects.all(), required=True)
    subject_id = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True)
    
    class Meta:
        model = Interest
        fields = [
            "interest_type_id",
            "student_id",
            "subject_id", 
        ]
        
class StudentRegisterFormAdmin(forms.ModelForm):
    admission_year = forms.IntegerField(required=True)
    personal_mail = forms.EmailField(required=False)
    phone_number = forms.IntegerField(required=False)
    curriculum_plan_id = forms.ModelChoiceField(
        queryset=CurriculumPlan.objects.all(), required=True
    )
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
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
        self.instance = kwargs.get("instance", None)
        super(StudentRegisterFormAdmin, self).__init__(*args, **kwargs)

    def clean_admission_year(self):
        admission_year = self.cleaned_data.get("admission_year")

        if not datetime.datetime.now().year >= admission_year >= 1980:
            raise forms.ValidationError("Year out of bounds")
        return admission_year

    def clean_personal_mail(self):
        email = self.cleaned_data.get("personal_mail")

        if email != "":
            if (
                Student.objects.filter(personal_mail=email).exists()
                and self.instance.personal_mail != email
            ):
                raise forms.ValidationError("This email is already used")
        return email

    def clean_phone_number(self):
        number = self.cleaned_data.get("phone_number")

        if number is not None:
            if (
                Student.objects.filter(phone_number=number).exists()
                and self.instance.number != number
            ):
                raise forms.ValidationError("This phone number is already used")
            elif len(str(number)) != 9:
                raise forms.ValidationError("The phone number must be 9 digits long")
        return number


class StudentInterest(forms.ModelForm):
    subject_id = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True)
    interest_type_id = forms.ModelChoiceField(
        queryset=InterestType.objects.all(), required=True
    )
    student_id = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        disabled=True,
        widget=forms.Select(attrs={"class": "hidden"}),
    )

    class Meta:
        model = Interest
        fields = [
            "subject_id",
            "interest_type_id",
            "student_id",
        ]

    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop("student_id", None)
        super(StudentInterest, self).__init__(*args, **kwargs)
        if student_id:
            self.fields["student_id"].initial = student_id
