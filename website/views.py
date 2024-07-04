from django.shortcuts import render, redirect, reverse
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth import views as auth_views
from django.db.models import Q, Subquery, OuterRef
from .utils import render_to_pdf, send_custom_email
from django.core.paginator import Paginator
from .forms import (
    StudentRegisterForm,
    UserRegisterForm,
    StudentRegisterFormAdmin,
    PeriodTypeFormAdmin,
    CurriculumPlanFormAdmin,
    InterestTypeFormAdmin,
    DegreeFormAdmin,
    AuthenticationFormWithInactiveUsersOkay,
    UserRegisterFormAdmin,
    StudentHistory,
    StudentInterest,
    HistoryFormAdmin,
    ContactFormAdmin,
    StudentProfilePicture,
    SubjectFormAdmin,
    InterestFormAdmin,
    SearchForm,
    MessageForm,
    UserPasswordUpdateFormAdmin,
    UserEditFormAdmin,
)
from .models import (
    Student,
    CurriculumPlan,
    Degree,
    User,
    PeriodType,
    InterestType,
    History,
    Interest,
    Subject,
    Contact,
)

from .decorators import role_required, anonymous_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import PasswordChangeForm

# Create your views here.


# Views
@login_required
def main_page(request):

    students = Student.objects.all()
    interests = Interest.objects.all()
    form = SearchForm()
    message_form = MessageForm(user=request.user)

    if request.method == "POST":
        if "search_form" in request.POST:
            form = SearchForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get("name")
                subj = form.cleaned_data.get("subject")
                interest_type = form.cleaned_data.get("interest_type")
                admission_year = form.cleaned_data.get("admission_year")

                if admission_year:
                    students = Student.objects.filter(admission_year=admission_year)

                # Se completa nombre pero no intereses
                if name and not interest_type and not subj:
                    students = students.filter(
                        Q(user__first_name__icontains=name)
                        | Q(user__last_name__icontains=name)
                    )

                # Se completan solo intereses pero no nombres
                elif not name and interest_type and subj:
                    interests = Interest.objects.filter(
                        interest_type_id=interest_type, subject_id=subj
                    ).values("student_id")
                    students = students.filter(id__in=Subquery(interests))

                # Se completa solo el interes
                elif not name and not subj and interest_type:
                    interests = Interest.objects.filter(
                        interest_type_id=interest_type,
                    ).values("student_id")
                    students = students.filter(id__in=Subquery(interests))

                # Se completa nombre e intereses
                elif name and interest_type and subj:
                    interests = Interest.objects.filter(
                        interest_type=interest_type, subject=subj
                    ).values("student_id")

                    students = students.filter(
                        (
                            Q(user__first_name__icontains=name)
                            | Q(user__last_name__icontains=name)
                        )
                        & Q(id__in=Subquery(interests))
                    )

        elif "message_form" in request.POST:
            receiver = User.objects.get(id=request.POST.get("id_receiver"))
            message_form = MessageForm(request.POST, user=request.user)
            if message_form.is_valid():
                send_custom_email(
                    request.user,
                    receiver,
                    message_form.cleaned_data.get("interest_type"),
                    message_form.cleaned_data.get("subject"),
                )

    paginator = Paginator(students, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "search_form": form,
        "page_obj": page_obj,
        "cant_pag": paginator.count,
        "students": students,
        "cant": len(students),
        "message_form": message_form,
    }

    return render(request, "website/main_page.html", context)


@role_required([User.ADMIN])
def admin_page(request, modelo=None):

    models = {
        "estudiante": Student,
        "usuario": User,
        "tipo_periodo": PeriodType,
        "plan_curricular": CurriculumPlan,
        "tipo_interes": InterestType,
        "carrera": Degree,
        "historial": History,
        "contacto": Contact,
        "curso": Subject,
        "interes": Interest,
    }

    forms = {
        "estudiante": StudentRegisterFormAdmin,
        "usuario": UserRegisterFormAdmin,
        "tipo_periodo": PeriodTypeFormAdmin,
        "plan_curricular": CurriculumPlanFormAdmin,
        "tipo_interes": InterestTypeFormAdmin,
        "carrera": DegreeFormAdmin,
        "historial": HistoryFormAdmin,
        "contacto": ContactFormAdmin,
        "curso": SubjectFormAdmin,
        "interes": InterestFormAdmin,
    }

    fields = {
        "estudiante": [
            "id",
            "admission_year",
            "personal_mail",
            "phone_number",
            "pfp",
            "user",
            "degree_id",
            "curriculum_plan_id",
        ],
        "usuario": [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "role",
        ],
        "tipo_periodo": ["id", "name"],
        "plan_curricular": ["id", "impl_year", "name", "degree_id"],
        "tipo_interes": ["id", "name"],
        "carrera": ["id", "name"],
        "historial": [
            "id",
            "year",
            "period",
            "interest_type_id",
            "subject_id",
            "student_id",
        ],
        "contacto": [
            "id",
            "message_type_id",
            "receiver_id",
            "sender_id",
            "subject_id",
        ],
        "curso": ["id", "name", "period", "period_type", "plan_id"],
        "interes": ["id", "interest_type_id", "student_id", "subject_id"],
    }

    editable_fields = {
        "estudiante": [
            "admission_year",
            "personal_mail",
            "phone_number",
            "user",
            "pfp",
            "degree_id",
            "curriculum_plan_id",
        ],
        "usuario": [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "role",
        ],
        "tipo_periodo": ["name"],
        "plan_curricular": ["name", "impl_year", "degree_id"],
        "tipo_interes": ["name"],
        "carrera": ["name"],
        "historial": ["year", "period", "interest_type_id", "subject_id", "student_id"],
        "contacto": [
            "message_type_id",
            "receiver_id",
            "sender_id",
            "subject_id",
        ],
        "curso": ["name", "period", "period_type", "plan_id"],
        "interes": ["interest_type_id", "student_id", "subject_id"],
    }

    if modelo not in models:
        return redirect("welcome")

    model = models[modelo]
    form_model = forms[modelo]
    password_form = UserPasswordUpdateFormAdmin()
    objs = model.objects.all()
    all_field_names = fields[modelo]
    form = form_model()
    editing = False
    id = None

    verbose_names = []
    for f in model._meta.fields:
        if f.name in all_field_names:
            verbose_names.append(f.verbose_name)

    if request.method == "POST":

        if "eliminar" in request.POST:
            model.objects.get(id=request.POST.get("id")).delete()

        elif "editar" in request.POST:
            obj = model.objects.get(id=request.POST.get("id"))

            if modelo == "usuario":
                form = UserEditFormAdmin(instance=obj)
            else:
                form = form_model(instance=obj)
            editing = True
            id = obj.id

        elif "guardar" in request.POST and not "password_form" in request.POST:
            # form = form_model(request.POST) # Se redeclara el form?
            if request.POST.get("editing") == "True":
                obj = model.objects.get(id=request.POST.get("id"))
                if modelo == "usuario":
                    form = UserEditFormAdmin(request.POST, request.FILES, instance=obj)
                else:
                    form = form_model(request.POST, request.FILES, instance=obj)
                if form.is_valid():
                    for field in editable_fields[modelo]:
                        if field != "pfp":
                            setattr(obj, field, form.cleaned_data[field])
                        elif field == "pfp":
                            if form.cleaned_data.get("pfp") is False:
                                setattr(obj, field, None)
                            else:
                                setattr(obj, field, form.cleaned_data[field])
                    obj.save()
                    editing = False
                    form = form_model()
            else:
                form = form_model(request.POST, request.FILES)
                if form.is_valid():
                    form.save()

        elif "password_form" in request.POST:
            print("hola como estan")
            print(f"HOLA 2: {request.POST.get("id_receiver")}")
            password_form = UserPasswordUpdateFormAdmin(request.POST)
            obj = model.objects.get(id=request.POST.get("id_receiver"))

            if password_form.is_valid():
                obj.set_password(password_form.cleaned_data["password"])
                obj.save()
            password_form = UserPasswordUpdateFormAdmin()

    context = {
        "model": model,
        "model_name": model._meta.verbose_name_plural,
        "model_fields": verbose_names,
        "objs": objs,
        "form": form,
        "editing": editing,
        "id": id,
        "raw_fields": all_field_names,
        "password_form": UserPasswordUpdateFormAdmin(),
        "model_queue": modelo,
    }

    return render(request, "website/admin_page.html", context)


@anonymous_required(redirect_url="/main_page/")
def do_login(request):
    if request.method == "POST":
        form = AuthenticationFormWithInactiveUsersOkay(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = auth.authenticate(username=username, password=password)

            if user:
                auth.login(request, user)
                if user.role == user.ADMIN:
                    return redirect(
                        reverse("admin_page", kwargs={"modelo": "estudiante"})
                    )
                else:
                    return redirect(reverse("main_page"))
        else:
            return render(request, "website/login.html", {"form": form})
    else:
        form = AuthenticationFormWithInactiveUsersOkay()
        return render(request, "website/login.html", {"form": form})


@login_required
def profile_page(request, id_user=None):
    user = User.objects.get(id=id_user)

    if user.role == user.STUDENT:
        degree = user.student.degree_id
        message_form = MessageForm(user=request.user)
        adm_year = user.student.admission_year
        pfp = user.student.pfp
        cplan = user.student.curriculum_plan_id
        student_history = History.objects.filter(student_id=user.student)
        student_help = Interest.objects.filter(
            student_id=user.student,
            interest_type_id=InterestType.objects.get(name="AUXILIO"),
        )
        student_tutor = Interest.objects.filter(
            student_id=user.student,
            interest_type_id=InterestType.objects.get(name="TUTORIA"),
        )
        student_ayud = Interest.objects.filter(
            student_id=user.student,
            interest_type_id=InterestType.objects.get(name="AYUDANTIA"),
        )
        form = StudentHistory(student_id=user.student)

        if request.method == "POST":
            if (
                "lista_aux" in request.POST
                or "lista_int" in request.POST
                or "lista_tutor" in request.POST
                or "lista_ayud" in request.POST
            ):
                model = Interest
            elif "lista_hist" in request.POST:
                model = History

            elif "message_form" in request.POST:
                receiver = User.objects.get(id=request.POST.get("id_receiver"))
                message_form = MessageForm(request.POST, user=request.user)
                if message_form.is_valid():
                    send_custom_email(
                        request.user,
                        receiver,
                        message_form.cleaned_data.get("interest_type"),
                        message_form.cleaned_data.get("subject"),
                    )

            if "eliminar" in request.POST:
                model.objects.get(id=request.POST.get("id")).delete()
            if "guardar" in request.POST:
                if "lista_hist" in request.POST:
                    form = StudentHistory(request.POST, student_id=user.student)
                elif "lista_int" in request.POST:
                    form = StudentInterest(request.POST, student_id=user.student)
                elif "pfp_estudiante" in request.POST:
                    form = StudentProfilePicture(
                        request.POST, request.FILES, instance=user.student
                    )
                if form.is_valid() and not "pfp_estudiante" in request.POST:
                    form.save()
                    # form = model(student_id=user.student) # ????
                else:
                    if form.is_valid():
                        if form.cleaned_data.get("pfp") is False:
                            user.student.pfp = None
                        else:
                            user.student.pfp = form.cleaned_data["pfp"]

                        user.student.save()
                        id_user = user.id
                        return redirect(
                            reverse(f"profile_page", kwargs={"id_user": id_user})
                        )

        context = {
            "user": user,
            "role": "Estudiante",
            "degree": degree,
            "year": adm_year,
            "pfp": pfp,
            "cplan": cplan,
            "history": student_history,
            "fields": ["año", "periodo", "ramo", "tipo"],
            "raw_fields": ["year", "period", "subject_id", "interest_type_id"],
            "form_history": StudentHistory(student_id=user.student),
            "help_list": student_help,
            "tutor_list": student_tutor,
            "ayud_list": student_ayud,
            "interest_fields": ["subject_id"],
            "form_interest": StudentInterest(student_id=user.student),
            "pfp_form": StudentProfilePicture(instance=user.student),
            "message_form": message_form,
        }

    elif user.role == user.PROFESSOR:
        context = {"user": user, "role": "Docente"}

    return render(request, "website/profile_page.html", context)


@login_required
def do_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("welcome")


def delete_user(request):
    user = request.user
    # solamente podemos borrar user si student no es referenciado en ningun lado, y su user no aparece en contact
    # solamente podemos borrar student si student no es referenciado en history o interest.
    delete_user = False
    delete_student = False
    if user.role == user.STUDENT:
        student = user.student
        if not student.history_set.exists() and not student.interest_set.exists():
            delete_student = True
        if not user.receiver.exists() and not user.sender.exists() and delete_student:
            delete_user = True
        # ahora, si delete_user es true entonces sabemos que delete estudent es true.
        if delete_user:
            # como tenemos on_delete = CASCADE solamente hay que borrar student, de ahi se borra todo lo demas
            student.delete()
            user.delete()
        # si no se puede borrar el usuario, a lo mejor solo se puede borrar estudiante
        elif delete_student:
            user.is_active = False  # desactivar el usuario, borrar estudiante?
            user.save()
        else:  # delete_user y delete_student son falsos a la vez
            user.is_active = False
            user.save()
    # borrar en caso docente
    elif user.role == user.PROFESSOR:
        if not user.receiver.exists() and not user.sender.exists():
            user.delete()
        else:
            user.is_active = False
            user.save()
    return redirect("logout")


def professor_edit(request):
    user = request.user
    editable_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "password1",
        "password2",
    ]

    if request.method == "POST":
        user_form = UserRegisterForm(
            request.POST, instance=User.objects.get(id=user.id)
        )

        email = request.POST.get("email")

        if not email.endswith("@utalca.cl"):
            user_form.add_error("email", "You must use your institution's email.")
            return render(
                request,
                "website/professor_edit.html",
                {
                    "user_form": user_form,
                },
            )

        if user_form.is_valid():
            user.role = User.PROFESSOR
            for field in editable_fields:
                if field != "password1" and field != "password2":
                    setattr(user, field, user_form.cleaned_data[field])
            user.save()
            if user == request.user:
                update_session_auth_hash(request, user)

            return redirect(reverse(f"profile_page", kwargs={"id_user": user.id}))
    else:
        user_form = UserRegisterForm(instance=User.objects.get(id=user.id))

    return render(
        request,
        "website/professor_edit.html",
        {
            "user_form": user_form,
        },
    )


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request, user
            )  # Actualiza la sesión del usuario si la contraseña ha cambiado
            messages.success(request, "Tu contraseña ha sido cambiada correctamente.")
            return redirect(
                reverse(f"profile_page", kwargs={"id_user": user.id})
            )  # Redirige a la página de perfil
        else:
            messages.error(request, "Por favor corrige los errores indicados.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "website/change_password.html", {"form": form})


def student_edit(request):

    user = request.user
    student = user.student

    student_editable_fields = [
        "admission_year",
        "personal_mail",
        "phone_number",
        "degree_id",
        "curriculum_plan_id",
    ]

    user_editable_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
    ]

    if request.method == "POST":
        user_form = UserRegisterForm(request.POST, instance=user)
        student_form = StudentRegisterForm(
            request.POST, request.FILES, instance=student, user=user
        )

        email = request.POST.get("email")

        if not email.endswith("@alumnos.utalca.cl"):
            user_form.add_error("email", "You must use your institution's email.")
            return render(
                request,
                "website/student_edit.html",
                {
                    "user_form": user_form,
                    "student_form": student_form,
                },
            )

        if user_form.is_valid() and student_form.is_valid():
            user.role = User.STUDENT

            for field in user_editable_fields:
                setattr(user, field, user_form.cleaned_data[field])
            user.save()

            for field in student_editable_fields:
                setattr(student, field, student_form.cleaned_data[field])
            student.user = user

            student.save()

            if user == request.user:
                update_session_auth_hash(request, user)

            return redirect(
                reverse(f"profile_page", kwargs={"id_user": request.user.id})
            )

    else:
        user_form = UserRegisterForm(instance=user)
        student_form = StudentRegisterForm(instance=student, user=user)

    return render(
        request,
        "website/student_edit.html",
        {
            "user_form": user_form,
            "student_form": student_form,
        },
    )


@anonymous_required(redirect_url="/main_page/")
def welcome(request):
    return render(request, "website/welcome.html")


@anonymous_required(redirect_url="/main_page/")
def register(request):
    return render(request, "website/register.html")


@anonymous_required(redirect_url="/main_page/")
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


@anonymous_required(redirect_url="/main_page/")
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


def generate_pdf(request, id_user=None):

    user = User.objects.get(id=id_user)
    student = user.student

    # ¿Que se puede poner en el pdf?
    # Historial
    # Intereses de ayudantias, tutorias y ramos
    # Cuando se unio la persona a la app?
    # Nombre y sus datos personales
    # Foto de perfil

    # Pasarla al context y luego mostrarla en el pdf

    degree = user.student.degree_id
    adm_year = user.student.admission_year
    pfp = user.student.pfp
    cplan = user.student.curriculum_plan_id
    student_history = History.objects.filter(student_id=user.student)

    student_tutor = Interest.objects.filter(
        student_id=user.student,
        interest_type_id=InterestType.objects.get(name="TUTORIA"),
    )

    student_help = Interest.objects.filter(
        student_id=user.student,
        interest_type_id=InterestType.objects.get(name="AUXILIO"),
    )

    student_ayud = Interest.objects.filter(
        student_id=user.student,
        interest_type_id=InterestType.objects.get(name="AYUDANTIA"),
    )

    context = {
        "user": user,
        "role": "Estudiante",
        "degree": degree,
        "year": adm_year,
        "pfp": pfp,
        "cplan": cplan,
        "history": student_history,
        "fields": ["año", "periodo", "ramo", "tipo"],
        "raw_fields": ["year", "period", "subject_id", "interest_type_id"],
        "form_history": StudentHistory(student_id=user.student),
        "help_list": student_help,
        "tutor_list": student_tutor,
        "ayud_list": student_ayud,
        "interest_fields": ["subject_id"],
        "form_interest": StudentInterest(student_id=user.student),
    }

    pdf = render_to_pdf("website/curriculum.html", context)
    if pdf:
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="curriculum_{user.username}.pdf"'
        )
        return response
    return HttpResponse("Error generating PDF")


def about_us(request):
    return render(request, "website/about_us.html")


def custom_404(request, exception):
    return render(request, "custom_404.html", status=404)


def load_cplans(request):
    degree_id = request.GET.get("degree_id")
    cplans = CurriculumPlan.objects.filter(degree_id=degree_id)

    return render(request, "website/cplan_options.html", {"cplans": cplans})
