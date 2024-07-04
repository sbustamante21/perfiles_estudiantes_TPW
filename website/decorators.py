from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # Redirige a la página de login si no está autenticado
            if request.user.role not in allowed_roles:
                return redirect("main_page")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def anonymous_required(function=None, redirect_url=None):
    if not redirect_url:
        redirect_url = '/'

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator