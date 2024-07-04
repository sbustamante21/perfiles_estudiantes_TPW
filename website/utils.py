import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime

from website.models import Contact, User

from django.core.mail import EmailMessage


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    # Use short variable names
    sUrl = settings.STATIC_URL  # Typically /static/
    sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL  # Typically /media/
    mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception("media URI must start with %s or %s" % (sUrl, mUrl))
    return path


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(
        BytesIO(html.encode("UTF-8")), result, link_callback=link_callback
    )
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None

def generate_year_choices(start_year=2000):
    current_year = datetime.now().year
    year_choices = [('', '------')]
    year_choices += [(year, year) for year in range(2000, current_year + 1)]
    return year_choices

# Enviar un correo entre un usuario y un
def send_custom_email(sender, receiver, int_type, subj):

    title = f"Contacto sobre {int_type.name} de {subj} en LinkICB"

    if sender.role == User.STUDENT:
        role = "Estudiante"
    elif sender.role == User.PROFESSOR:
        role = "Docente"
    else: # Esto nunca debiera suceder pero igual va
        role = "Admin"
    
    if role == "Estudiante":
        degree = sender.student.degree_id.name
    else:
        degree = None

    context = {
        "sender": sender,
        "receiver": receiver,
        "int_type": int_type.name.lower(),
        "role": role,
        "degree":degree,
        "subject": subj,
        "title": title,
        "action": "necesito" if int_type.name == "AUXILIO" else "ofrezco",
    }

    html_message = render_to_string("website/email_template.html", context)

    email = EmailMessage(title, html_message, "linkicb1@gmail.com", [receiver.email])

    email.content_subtype = "html"
    email.send()

    # Guardar en la tabla de contacto la interaccion
    new_contact = Contact(
        message_type_id=int_type,
        subject_id=subj,
        receiver_id=receiver,
        sender_id=sender,
    )

    new_contact.save()
