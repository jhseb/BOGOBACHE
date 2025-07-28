from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bache
from reportes.models import Reporte  # Asegúrate de importar correctamente
from bache.models import Bache
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Bache)
def notificar_modificacion_bache(sender, instance, created, **kwargs):
    if created:
        # No hacer nada si es un Bache nuevo
        return

    # Obtener todos los usuarios únicos que tienen reportes asociados al bache
    reportes = Reporte.objects.filter(bache=instance).select_related('usuario')
    correos = list(set([r.usuario.email for r in reportes if r.usuario and r.usuario.email]))

    if correos:
        asunto = f"Actualización del bache #{instance.id_bache}"
        mensaje = f"El bache con ID {instance.id_bache} ha sido actualizado al estado: {instance.estado}."
        remitente = settings.DEFAULT_FROM_EMAIL  # Asegúrate de que esté definido en settings.py

        send_mail(
            asunto,
            mensaje,
            remitente,
            correos,
            fail_silently=False,
        )


@receiver(post_save, sender=Bache)
def actualizar_estado_reportes(sender, instance, created, **kwargs):
    """
    Al guardar un bache, si el estado cambia, se actualizan los reportes relacionados
    y se notifica por correo a los usuarios que reportaron ese bache.
    """
    if created:
        return  # No hacer nada si el bache es nuevo

    try:
        bache_anterior = Bache.objects.get(pk=instance.pk)
    except Bache.DoesNotExist:
        return

    # Compara si el estado cambió
    if bache_anterior.estado != instance.estado:
        # Obtiene todos los reportes relacionados con este bache
        reportes = Reporte.objects.filter(bache=instance).select_related('usuario')

        # Extrae los correos de los usuarios conectados a esos reportes
        correos = list(set(
            r.usuario.email for r in reportes
            if r.usuario and r.usuario.email
        ))

        if correos:
            send_mail(
                subject=f"Actualización del Bache #{instance.id_bache}",
                message=f"El bache con ID {instance.id_bache} ha sido actualizado a estado: {instance.estado}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=correos,
                fail_silently=False,
            )

        # Opcional: actualizar estado de los reportes también
        for reporte in reportes:
            reporte.estado = instance.estado
            reporte.save()


@receiver(post_save, sender=Reporte)
def incrementar_accidentes_bache(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo reporte, incrementa en 1 el contador de accidentes del bache asociado.
    """
    if created and instance.bache and instance.involucrado_reporte:
        bache = instance.bache
        bache.accidentes += 1
        bache.save()