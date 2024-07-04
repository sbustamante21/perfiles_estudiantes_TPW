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
