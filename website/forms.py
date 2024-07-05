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
    Contact,
)
from django.core.validators import MaxValueValidator
import datetime
from .utils import generate_year_choices


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
    subject_id = forms.ModelChoiceField(
        queryset=Subject.objects.all(), required=True, label="Curso"
    )
    interest_type_id = forms.ModelChoiceField(
        queryset=InterestType.objects.exclude(name="AUXILIO"),
        required=True,
        label="Tipo interés",
    )
    year = forms.ChoiceField(
        choices=generate_year_choices(), required=True, label="Año"
    )
    period = forms.ChoiceField(choices=NUMBER_CHOICES, required=True, label="Semestre")
    student_id = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput(),
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
        year = int(self.cleaned_data.get("year"))

        if not datetime.datetime.now().year >= year >= 1980:
            raise forms.ValidationError("Año no disponible.")
        return year


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, label="Nombre de usuario")
    email = forms.EmailField(required=True, label="Correo institucional")
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Oculta los campos de contraseña si se está editando un usuario existente
        if kwargs.get("instance"):
            self.fields.pop("password1")
            self.fields.pop("password2")
    
    def clean_first_name(self):
        return self.cleaned_data.get("first_name").lower()

    def clean_username(self):
        username = self.cleaned_data.get("username")
        existing_users = User.objects.filter(username=username)
        if self.instance:
            existing_users = existing_users.exclude(pk=self.instance.pk)
        if existing_users.exists():
            raise forms.ValidationError(
                "Este nombre de usuario ya está en uso."
            )
        return username

    def clean_last_name(self):
        return self.cleaned_data.get("last_name").lower()

    def clean_email(self):
        email = self.cleaned_data.get("email")

        existing_users = User.objects.filter(email=email)
        if self.instance:
            # Exclude the current instance from the existing users
            existing_users = existing_users.exclude(pk=self.instance.pk)
        if existing_users.exists():
            raise forms.ValidationError("Este correo ya está registrado.")

        return email


class UserPasswordUpdateFormAdmin(forms.ModelForm):

    class Meta:
        model = User
        fields = ["password"]

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance", None)
        super(UserPasswordUpdateFormAdmin, self).__init__(*args, **kwargs)


class UserRegisterFormAdmin(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True, label="Nombre de usuario")
    email = forms.EmailField(required=True, label="Correo institucional")
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    is_active = forms.BooleanField(required=False, initial=True, label="Activo")
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Rol")

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

    def clean_first_name(self):
        return self.cleaned_data.get("first_name").lower()

    def clean_last_name(self):
        return self.cleaned_data.get("last_name").lower()

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists() and self.instance.email != email:
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password"]
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserEditFormAdmin(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True, label="Nombre de usuario")
    email = forms.EmailField(required=True, label="Correo institucional")
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    is_active = forms.BooleanField(required=False, initial=True, label="Activo")
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Rol")

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
        exclude = ["password"]

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance", None)
        super(UserEditFormAdmin, self).__init__(*args, **kwargs)
    
    def clean_first_name(self):
        return self.cleaned_data.get("first_name").lower()

    def clean_last_name(self):
        return self.cleaned_data.get("last_name").lower()

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists() and self.instance.email != email:
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class StudentRegisterForm(forms.ModelForm):
    admission_year = forms.ChoiceField(
        choices=generate_year_choices(), required=True, label="Año de ingreso"
    )
    personal_mail = forms.EmailField(required=False, label="Correo personal (opcional)")
    phone_number = forms.IntegerField(required=False, label="Número de teléfono (opcional)")
    degree_id = forms.ModelChoiceField(
        queryset=Degree.objects.all(),
        required=True,
        label="Carrera",
        widget=forms.Select(
            attrs={"hx-get": "../load_cplans", "hx-target": "#id_curriculum_plan_id"}
        ),
    )
    curriculum_plan_id = forms.ModelChoiceField(
        queryset=CurriculumPlan.objects.none(), required=True, label="Plan curricular"
    )

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

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance", None)
        self.user = kwargs.pop("user", None)
        super(StudentRegisterForm, self).__init__(*args, **kwargs)

        if "degree_id" in self.data:
            degree_id = self.data.get("degree_id")
            if degree_id != "":
                self.fields["curriculum_plan_id"].queryset = CurriculumPlan.objects.filter(
                    degree_id=degree_id
                )

    def clean_admission_year(self):
        admission_year = self.cleaned_data.get("admission_year")

        if not datetime.datetime.now().year >= int(admission_year) >= 1980:
            raise forms.ValidationError("Año fuera de límites.")
        return admission_year

    def clean_personal_mail(self):
        email = self.cleaned_data.get("personal_mail")

        if email != "":
            if (
                Student.objects.filter(personal_mail=email)
                .exclude(user=self.user)
                .exists()
            ):
                raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_phone_number(self):
        number = self.cleaned_data.get("phone_number")

        if number is not None:
            if (
                Student.objects.filter(phone_number=number)
                .exclude(user=self.user)
                .exists()
            ):
                raise forms.ValidationError("Este número de teléfono ya está registrado.")
            elif len(str(number)) != 9:
                raise forms.ValidationError("El número de teléfono debe tener 9 dígitos.")
        return number


class StudentProfilePicture(forms.ModelForm):
    pfp = forms.ImageField(required=False, label="Foto de Perfil")

    class Meta:
        model = Student
        fields = ["pfp"]

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance", None)
        super(StudentProfilePicture, self).__init__(*args, **kwargs)


class PeriodTypeFormAdmin(forms.ModelForm):
    name = forms.CharField(required=True, label="Nombre del tipo de período")

    class Meta:
        model = PeriodType
        fields = [
            "name",
        ]
    
    def clean_name(self):
        name = self.cleaned_data.get("name").upper()
        return name


class CurriculumPlanFormAdmin(forms.ModelForm):
    name = forms.CharField(required=True, label="Nombre del plan curricular")
    impl_year = forms.IntegerField(required=True, label="Año de implementación")
    degree_id = forms.ModelChoiceField(
        queryset=Degree.objects.all(), required=True, label="Carrera"
    )

    def clean_name(self):
        name = self.cleaned_data.get("name").upper()
        return name

    class Meta:
        model = CurriculumPlan
        fields = [
            "name",
            "impl_year",
            "degree_id",
        ]


class InterestTypeFormAdmin(forms.ModelForm):
    name = forms.CharField(required=True, label="Nombre del tipo de interés")

    class Meta:
        model = InterestType
        fields = [
            "name",
        ]
    
    def clean_name(self):
        name = self.cleaned_data.get("name").upper()
        return name


class DegreeFormAdmin(forms.ModelForm):
    name = forms.CharField(required=True, label="Nombre de la carrera")

    class Meta:
        model = Degree
        fields = [
            "name",
        ]

    def clean_name(self):
        name = self.cleaned_data.get("name").upper()
        return name


class SubjectFormAdmin(forms.ModelForm):
    NUMBER_CHOICES = [
        (1, "1"),
        (2, "2"),
    ]
    name = forms.CharField(required=True, label="Nombre del curso")
    period = forms.ChoiceField(
        choices=NUMBER_CHOICES, required=True, label="Período (semestre)"
    )
    period_type = forms.ModelChoiceField(
        queryset=PeriodType.objects.all(), required=True, label="Tipo de período"
    )
    plan_id = forms.ModelChoiceField(
        queryset=CurriculumPlan.objects.all(), required=True, label="Plan curricular"
    )

    class Meta:
        model = Subject
        fields = [
            "name",
            "period",
            "period_type",
            "plan_id",
        ]

    def clean_name(self):
        name = self.cleaned_data.get("name").upper()
        return name


class HistoryFormAdmin(forms.ModelForm):
    NUMBER_CHOICES = [
        (1, "1"),
        (2, "2"),
    ]
    year = forms.IntegerField(required=True, label="Año")
    period = forms.ChoiceField(choices=NUMBER_CHOICES, required=True, label="Semestre")
    interest_type_id = forms.ModelChoiceField(
        queryset=InterestType.objects.all(), required=True, label="Tipo de interés"
    )
    subject_id = forms.ModelChoiceField(
        queryset=Subject.objects.all(), required=True, label="Curso"
    )
    student_id = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=True,
        label="Correo del estudiante (Identificador)",
    )

    class Meta:
        model = History
        fields = [
            "year",
            "period",
            "interest_type_id",
            "subject_id",
            "student_id",
        ]


class ContactFormAdmin(forms.ModelForm):

    message_type_id = forms.ModelChoiceField(
        queryset=InterestType.objects.all(),
        required=True,
        label="Tipo de mensaje, según interés",
    )
    receiver_id = forms.ModelChoiceField(
        queryset=User.objects.all(), required=True, label="Usuario destinatario"
    )
    sender_id = forms.ModelChoiceField(
        queryset=User.objects.all(), required=True, label="Usuario remitente"
    )
    subject_id = forms.ModelChoiceField(
        queryset=Subject.objects.all(), required=True, label="Curso"
    )

    class Meta:
        model = Contact
        fields = [
            "message_type_id",
            "receiver_id",
            "sender_id",
            "subject_id",
        ]


class InterestFormAdmin(forms.ModelForm):
    interest_type_id = forms.ModelChoiceField(
        queryset=InterestType.objects.all(), required=True
    )
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
    admission_year = forms.IntegerField(required=True, label="Año de ingreso")
    personal_mail = forms.EmailField(required=False, label="Correo personal")
    phone_number = forms.IntegerField(required=False, label="Número de teléfono")
    degree_id = forms.ModelChoiceField(
        queryset=Degree.objects.all(),
        required=True,
        label="Carrera",
        widget=forms.Select(
            attrs={
                "hx-get": "../../../load_cplans",
                "hx-target": "#id_curriculum_plan_id",
            }
        ),
    )
    curriculum_plan_id = forms.ModelChoiceField(
        queryset=CurriculumPlan.objects.none(), required=True, label="Plan curricular"
    )

    user = forms.ModelChoiceField(
        queryset=User.objects.all(), required=True, label="Nombre de usuario"
    )
    pfp = forms.ImageField(required=False, label="Foto de perfil")

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

        if "degree_id" in self.data:
            degree_id = self.data.get("degree_id")
            self.fields["curriculum_plan_id"].queryset = CurriculumPlan.objects.filter(
                degree_id=degree_id
            )

    def clean_admission_year(self):
        admission_year = self.cleaned_data.get("admission_year")

        if not datetime.datetime.now().year >= admission_year >= 1980:
            raise forms.ValidationError("Año no disponible.")
        return admission_year

    def clean_personal_mail(self):
        email = self.cleaned_data.get("personal_mail")

        if email != "":
            if (
                Student.objects.filter(personal_mail=email).exists()
                and self.instance.personal_mail != email
            ):
                raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_phone_number(self):
        number = self.cleaned_data.get("phone_number")

        if number is not None:
            if (
                Student.objects.filter(phone_number=number).exists()
                and self.instance.phone_number != number
            ):
                raise forms.ValidationError("Este número de teléfono ya está registrado.")
            elif len(str(number)) != 9:
                raise forms.ValidationError("El número de teléfono debe tener 9 dígitos.")
        return number


class StudentInterest(forms.ModelForm):
    subject_id = forms.ModelChoiceField(
        queryset=Subject.objects.all(), required=True, label="Curso"
    )
    interest_type_id = forms.ModelChoiceField(
        queryset=InterestType.objects.all(), required=True, label="Tipo de interés"
    )
    student_id = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput(),
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


class SearchForm(forms.Form):
    name = forms.CharField(max_length=100, required=False, label="Nombre")
    interest_type = forms.ModelChoiceField(
        queryset=InterestType.objects.all(), required=False, label="Tipo de interés"
    )

    degree_id = forms.ModelChoiceField(queryset=Degree.objects.all(), required=False, label="Carrera",
    widget=forms.Select(attrs={"hx-get":"../load_cplans/", "hx-target":  "#id_cplan",}),)

    cplan = forms.ModelChoiceField(queryset=CurriculumPlan.objects.none(), required=False, label="Plan curricular",
    widget=forms.Select(attrs={"hx-get":"../load_subjects/", "hx-target": "#id_subject"}),)

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(), required=False, label="Curso"
    )

    admission_year = forms.ChoiceField(
        choices=generate_year_choices(), required=False, label="Año de ingreso"
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance", None)
        super(SearchForm, self).__init__(*args, **kwargs)

        if "degree_id" in self.data:
            degree_id = self.data.get("degree_id")
            if degree_id != "":
                self.fields["cplan"].queryset = CurriculumPlan.objects.filter(degree_id=degree_id)

        if "cplan" in self.data:
            cplan = self.data.get("cplan")
            if cplan != "":
                self.fields["subject"].queryset = Subject.objects.filter(
                        plan_id=cplan
                    )


class MessageForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(), required=True, label="Ramo"
    )
    interest_type = forms.ModelChoiceField(
        queryset=InterestType.objects.all(), required=True, label="Tipo de interés"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(MessageForm, self).__init__(*args, **kwargs)

        if user.role == User.PROFESSOR:
            self.fields["interest_type"].queryset = InterestType.objects.filter(
                name="AYUDANTIA"
            )
        elif user.role == User.STUDENT:
            self.fields["interest_type"].queryset = InterestType.objects.exclude(
                name="AYUDANTIA"
            )
