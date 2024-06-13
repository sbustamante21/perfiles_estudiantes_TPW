from django.shortcuts import render, redirect, reverse
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from .forms import StudentRegisterForm, UserRegisterForm, StudentRegisterFormAdmin, PeriodTypeFormAdmin, CurriculumPlanFormAdmin, InterestTypeFormAdmin
from .models import Student, CurriculumPlan, Degree, User, PeriodType, InterestType
from django.contrib.auth.views import LogoutView

# Create your views here.


# Views
@login_required
def main_page(request):
    return render(request, "website/main_page.html", {})

@login_required
def admin_page(request, modelo=None):

    models = {
        "estudiante": Student,
        "usuarios": User, 
        "tipo_periodo": PeriodType,
        "plan_curricular": CurriculumPlan,
        "tipo_interes" : InterestType,
    }

    forms = {
        "estudiante": StudentRegisterFormAdmin,
        "user": UserRegisterForm,
        "tipo_periodo": PeriodTypeFormAdmin,
        "plan_curricular": CurriculumPlanFormAdmin,
        "tipo_interes" : InterestTypeFormAdmin,
    }

    fields = {
        "estudiante": ["id", "admission_year", "personal_mail", "phone_number", "pfp", "user", "degree_id", "curriculum_plan_id"],
        "tipo_periodo": ["id", "name"],
        "plan_curricular": ["id", "name", "impl_year", "degree_id"],
        "tipo_interes": ["id", "name"],
    }

    editable_fields = {
        "estudiante": ["admission_year", "personal_mail", "phone_number", "user", "pfp", "degree_id", "curriculum_plan_id"],
        "tipo_periodo": ["name"],
        "plan_curricular": ["name", "impl_year", "degree_id"],
        "tipo_interes": ["name"],
    }

    if modelo not in models:
        return redirect("welcome")

    model = models[modelo]
    form_model = forms[modelo]
    objs = model.objects.all()
    all_field_names = fields[modelo]
    form = form_model()
    editing = False
    id = None

    if request.method == "POST":

        if "eliminar" in request.POST:
            model.objects.get(id=request.POST.get("id")).delete()

        elif "editar" in request.POST:
            obj = model.objects.get(id=request.POST.get("id"))
            form = form_model(instance=obj)
            editing = True
            id = obj.id

        elif "guardar" in request.POST:
            #form = form_model(request.POST) # Se redeclara el form?
            if request.POST.get("editing") == "True":
                obj = model.objects.get(id=request.POST.get("id"))
                form = form_model(request.POST, instance=obj)
                if form.is_valid():
                    for field in editable_fields[modelo]:
                        setattr(obj, field, form.cleaned_data[field])
                    obj.save()
                    editing=False
                    form = form_model()
            else:
                form = form_model(request.POST)
                if form.is_valid():
                    form.save()
                    form = form_model()

    context = {"model": model, "model_name":model._meta.verbose_name_plural, "model_fields":model._meta.fields, "objs":objs, "form":form, "editing":editing, "id":id, "raw_fields": all_field_names}
    return render(request, "website/admin_page.html", context)

def do_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                if user.role == user.ADMIN:
                    return redirect(
                        reverse("admin_page", kwargs={"modelo": "estudiante"})
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
        cplan = user.student.curriculum_plan_id
        context = {"user": user, "role": "Estudiante", "degree":degree, "year":adm_year, "pfp":pfp, "cplan":cplan}
    elif user.role == user.PROFESSOR:
        context = {"user":user, "role":"Docente"}

    return render(request, "website/profile_page.html", context)


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
            user.is_active = False # desactivar el usuario, borrar estudiante?
            user.save()
        else: # delete_user y delete_student son falsos a la vez
            user.is_active = False
            user.save()
    # borrar en caso docente
    elif user.role == user.PROFESSOR:
        if not user.receiver.exists() and not user.sender.exists():
            user.delete()
        else: 
            user.is_active = False
            user.save()
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
