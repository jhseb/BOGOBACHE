from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReporteForm
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required
from usuario.models import Usuario 
from bache.models import Bache  

from .models import Reporte
import json

@login_required
@xframe_options_exempt
def crear_reportes(request):
    es_popup = request.GET.get('popup') == '1'
    id_bache = request.GET.get('id_bache')

    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.involucrado_reporte = True  # por defecto en True

            try:
                usuario = Usuario.objects.get(cedula=request.user.username)
                reporte.usuario = usuario
            except Usuario.DoesNotExist:
                return render(request, 'error.html', {
                    'mensaje': 'Usuario no encontrado. Asegúrate de que el usuario tenga cédula registrada.'
                })

            if id_bache:
                bache = get_object_or_404(Bache, id_bache=id_bache)
                reporte.bache = bache

                # Si ya hay al menos un reporte, sumamos 1 al contador de accidentes
                if Reporte.objects.filter(bache=bache).exists():
                    bache.save()

            reporte.save()

            return render(
                request,
                'reportes/crear_reporte_popup.html' if es_popup else 'reportes/crear_reporte_usuario.html',
                {
                    'form': ReporteForm(),
                    'es_popup': es_popup,
                    'guardado': True,
                    'id_bache': id_bache
                }
            )
        else:
            errores = {field: [str(e) for e in errores] for field, errores in form.errors.items()}
            return render(
                request,
                'reportes/crear_reporte_popup.html' if es_popup else 'reportes/crear_reporte_usuario.html',
                {
                    'form': form,
                    'es_popup': es_popup,
                    'errores_formulario': json.dumps(errores),
                    'id_bache': id_bache
                }
            )
    else:
        form = ReporteForm()
        return render(
            request,
            'reportes/crear_reporte_popup.html' if es_popup else 'reportes/crear_reporte_usuario.html',
            {
                'form': form,
                'es_popup': es_popup,
                'id_bache': id_bache
            }
        )


@login_required
def consultar_reportes(request):
    try:
        #usuario = Usuario.objects.get(cedula=request.user.username)
        usuario = Usuario.objects.get(cedula=request.user.username)
        reportes = Reporte.objects.filter(usuario=usuario)

        return render(request, 'reportes/consultar_reportes.html', {
            'reportes': reportes
        })
    except Usuario.DoesNotExist:
        return render(request, 'error.html', {
            'mensaje': 'Usuario no encontrado. Asegúrate de que el usuario tenga cédula registrada.'
        })

@login_required
def ver_reporte_detalle(request, id_reporte):
    reporte = get_object_or_404(Reporte, pk=id_reporte)

    try:
        usuario = Usuario.objects.get(cedula=request.user.username)
    except Usuario.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'Usuario no válido'})

    if reporte.usuario != usuario:
        return render(request, 'error.html', {'mensaje': 'No tiene permiso para ver este reporte.'})

    # Crear el formulario con la instancia
    form = ReporteForm(instance=reporte)

    # Deshabilitar todos los campos
    for field in form.fields.values():
        field.disabled = True

    return render(request, 'reportes/ver_reporte.html', {
        'form': form,
        'modo_lectura': True
    })