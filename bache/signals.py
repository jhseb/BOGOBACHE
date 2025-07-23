from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Bache
#from reportes.models import Reporte# <- Importas desde la otra app

@receiver(post_save, sender=Bache)
def actualizar_estado_reporte(sender, instance, **kwargs):
    try:
        # Buscar el reporte relacionado al bache actualizado
        reporte = Reporte.objects.get(bache=instance)

        # Actualizar campo estado en Reporte desde Bache
        reporte.estado = instance.estado
        reporte.save()
        
        # ← Aquí dejas el valor en una variable visible (si es necesario para debug o pruebas)
        estado_actualizado = instance.estado
        print("Estado actualizado del bache:", estado_actualizado)

    except Reporte.DoesNotExist:
        # Si no hay reporte asociado, no hacer nada o registrar un log
        print(f"No hay reporte asociado al bache {instance.id}")