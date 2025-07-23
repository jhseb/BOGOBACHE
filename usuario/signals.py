from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario  # Asegúrate que sea el modelo correcto
from reportes.models import Reporte  # Importa correctamente el modelo Reporte

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
