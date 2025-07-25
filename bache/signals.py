from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bache
from reportes.models import Reporte  # Asegúrate de importar correctamente
from bache.models import Bache
@receiver(post_save, sender=Bache)
def actualizar_estado_reportes(sender, instance, **kwargs):
    """
    Al guardar un bache, actualiza el estado de todos los reportes relacionados.
    Si no hay reportes, no hace nada.
    """
    reportes = Reporte.objects.filter(bache=instance)

    if reportes.exists():
        for reporte in reportes:
            reporte.estado = instance.estado
            reporte.save()
@receiver(post_save, sender=Reporte)
def incrementar_accidentes_bache(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo reporte, incrementa en 1 el contador de accidentes del bache asociado.
    """
    if created and instance.bache:
        bache = instance.bache
        bache.accidentes += 1
        bache.save()