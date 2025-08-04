from django.core.validators import RegexValidator
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib import admin
from django.conf import settings

class Usuario(models.Model):
    cedula = models.CharField(
        primary_key=True,
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='La cédula debe tener exactamente 10 dígitos numéricos.'
            )
        ],
        verbose_name="Cédula o Nombre de Usuario"
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    localidad = models.CharField(max_length=100)
    ciudad_origen = models.CharField(max_length=100, verbose_name="Ciudad de Origen")  # Campo agregado
    telefono = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='El teléfono debe tener exactamente 10 dígitos numéricos.'
            )
        ],
        verbose_name="Teléfono"  # Campo agregado
    )
    medio_trans = models.CharField(max_length=100, verbose_name="Medio de Transporte")
    email = models.EmailField()
    notificacion = models.BooleanField(default=False, verbose_name="¿Desea recibir notificaciones?")
    rol = models.IntegerField(verbose_name="Rol del Usuario")

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula})"


class Servicio(models.Model):
    id_request = models.CharField(
        primary_key=True,
        max_length=50, 
        verbose_name="ID de Solicitud"
    )
    cedula = models.ForeignKey(
        'Usuario',  # Asegúrate que 'Usuario' esté definido en el mismo archivo o importa correctamente
        to_field='cedula',
        on_delete=models.CASCADE,
        verbose_name="Cédula o Nombre de Usuario"
    )
    tipo = models.CharField(max_length=100)
    valor = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    respuesta = models.TextField(blank=True, null=True)
    fecha_solicitud = models.DateTimeField(
        verbose_name="Fecha de Solicitud"
    )
    estado = models.CharField(
        max_length=100,
        verbose_name="Estado"
    )

    def __str__(self):
        return f"Servicio {self.id_request} - Usuario: {self.cedula}"



class Documento(models.Model):
    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='pdfs/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
class Documento_admin(models.Model):
    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='pdfs/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class RegistroSesion(models.Model):
    username = models.ForeignKey(
        'Usuario', 
        to_field='cedula',
        on_delete=models.CASCADE,
        verbose_name="Cédula o Nombre de Usuario"
    )
    fecha_login = models.DateTimeField(default=now)
    fecha_logout = models.DateTimeField(null=True, blank=True)
    duracion = models.CharField(max_length=20, null=True, blank=True)