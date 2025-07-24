from django.core.validators import RegexValidator
from django.db import models

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
    medio_trans = models.CharField(max_length=100, verbose_name="Medio de Transporte")
    email = models.EmailField()
    notificacion = models.BooleanField(default=False, verbose_name="¿Desea recibir notificaciones?")
    rol = models.IntegerField(verbose_name="Rol del Usuario")

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula})"


from django.db import models
from datetime import datetime

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

