
# Register your models here.
from django.contrib import admin
from .models import RegistroSesion

@admin.register(RegistroSesion)
class RegistroSesionAdmin(admin.ModelAdmin):
    list_display = ("username", "fecha_login", "fecha_logout", "duracion")