from django.contrib import admin
from django.apps import apps

# Register your models here.

def auto_register(model):
    #Get all fields from model, but exclude autocreated reverse relations
    field_list = [f.name for f in model._meta.get_fields() if f.auto_created == False]
    # Dynamically create ModelAdmin class and register it.
    my_admin = type('MyAdmin', (admin.ModelAdmin,), 
                        {'list_display':field_list }
                        )
    try:
        admin.site.register(model,my_admin)
    except AlreadyRegistered:
        # This model is already registered
        pass

for model in apps.get_app_config('website').get_models():
    auto_register(model)

