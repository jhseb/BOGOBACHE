from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario  # Asegúrate que sea el modelo correcto
from reportes.models import Reporte  # Importa correctamente el modelo Reporte
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import RegistroSesion
from django.utils.timezone import now

@receiver(post_save, sender=Usuario)
def actualizar_email_reporte(sender, instance, **kwargs):
    try:
        reportes = Reporte.objects.filter(usuario=instance)

        if reportes.exists():
            for reporte in reportes:
                reporte.email = instance.email
                reporte.save()

            print(f"Se actualizaron los emails de los reportes del usuario {instance.pk}")
    except Exception as e:
        print(f"Error al actualizar los emails de los reportes del usuario {instance.pk}: {str(e)}")




@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    RegistroSesion.objects.create(
        username=user.username,
        fecha_login=now()
    )


@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):
    ultima_sesion = RegistroSesion.objects.filter(
        username=user.username, fecha_logout__isnull=True
    ).last()

    if ultima_sesion:
        ultima_sesion.fecha_logout = now()

        # Calcular diferencia
        diferencia = ultima_sesion.fecha_logout - ultima_sesion.fecha_login
        total_segundos = int(diferencia.total_seconds())
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        segundos = total_segundos % 60

        # Guardar directamente como HH:MM:SS
        ultima_sesion.duracion = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        ultima_sesion.save()
