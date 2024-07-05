from django import template
from website.models import User


register = template.Library()


@register.filter
def attr(obj, field):
    return getattr(obj, field)


@register.filter
def display_role(value, field_name):
    if field_name == "role" and isinstance(value, int):
        rolename = dict(User.ROLE_CHOICES).get(value, "Unknown")
        if rolename == "Student":
            return "Estudiante"
        elif rolename == "Professor":
            return "Docente"
        elif rolename == "Admin":
            return rolename
    return value


@register.filter
def parse_name(name):
    return name.title()


@register.filter
def make_upper(value):
    return value.upper()


@register.filter
def model_translated(model_name):
    if model_name == "students":
        return "Estudiantes"
    elif model_name == "period types":
        return "Tipo de Período"
    elif model_name == "curriculum plans":
        return "Plan curricular"
    elif model_name == "interest types":
        return "Tipo de Interés"
    elif model_name == "degrees":
        return "Carrera"
    elif model_name == "usuarios":
        return "Usuarios"
    elif model_name == "historys":
        return "Historiales"
    elif model_name == "contacts":
        return "Contactos"
    elif model_name == "subjects":
        return "Ramos"
    elif model_name == "interests":
        return "Intereses"


@register.filter
def field_translated(field_name):

    trads = {
        "admission_year": "Año de admisión",
        "personal_mail": "Correo personal",
        "phone_numer": "Número de teléfono",
        "pfp": "Foto de perfil",
        "user": "Usuario",
        "degree id": "Carrera",
        "curriculum plan id": "Plan curricular",
        "name": "Nombre",
        "impl_year": "Año",
        "role": "Role",
        "year": "Año",
        "period": "Período",
        "interest type id": "Tipo de periodo",
        "subject id": "Ramo",
        "student id": "Estudiante",
        "message type id": "Tipo de mensaje",
        "receiver id": "Destinatario",
        "sender id": "Emisor",
        "plan id": "Plan curricular",
        "ID": "ID",
    }
    if not field_name in trads.keys():
        return field_name.capitalize()

    return trads[field_name]
