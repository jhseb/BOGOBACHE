from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReporteForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from django.urls import reverse
from django.utils.timezone import now
from django.utils.timezone import make_aware
from datetime import datetime
from usuario.models import Usuario 
from bache.models import Bache, Localidad, UPZ, Barrio, Estado, Tipo_calle, Profundidad
from .models import Reporte
import json
from django.http import JsonResponse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from . import views
from datetime import datetime, timedelta
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

                # Validar si ya existe un reporte para este usuario y bache con involucrado_reporte=False
                  # ⚠️ Validar si ya está conectado como observador
                if Reporte.objects.filter(bache=bache, usuario=usuario, involucrado_reporte=False, deleted_at__isnull=True).exists():
                    return render(request, 'reportes/crear_reporte_popup.html', {
                        'form': form,
                        'es_popup': True,
                        'id_bache': id_bache,
                        'ya_conectado': True
                    })

                # Si ya hay al menos un reporte, puedes hacer lógica adicional aquí si quieres
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
        usuario = Usuario.objects.get(cedula=request.user.username)
        involucrado = request.GET.get('involucrado')  # '1', '0' o None

        reportes =Reporte.objects.filter(usuario=usuario, deleted_at__isnull=True)

        if involucrado == '1':
            reportes = reportes.filter(usuario=usuario, involucrado_reporte=True)
        elif involucrado == '0':
            reportes = reportes.filter(usuario=usuario, involucrado_reporte=False)

        return render(request, 'reportes/consultar_reportes.html', {
            'reportes': reportes,
            'involucrado': involucrado  # enviamos esto al template para marcar la opción seleccionada
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

@login_required
def ver_reporte_detalle_admin(request, id_reporte):
    # Buscar el reporte por clave primaria
    reporte = get_object_or_404(Reporte, pk=id_reporte)

    # Crear el formulario con los datos del reporte
    form = ReporteForm(instance=reporte)

    # Deshabilitar los campos (modo lectura)
    for field in form.fields.values():
        field.disabled = True

    return render(request, 'reportes/ver_reporte_admin.html', {
        'form': form,
        'modo_lectura': True,
        'reporte': reporte,  
    })

@login_required
@xframe_options_exempt
def crear_reporte_simple(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bache_id = data.get('bache_id')

            if not bache_id:
                return JsonResponse({'success': False, 'error': 'ID de bache no proporcionado'})

            bache = Bache.objects.get(id_bache=bache_id)
            usuario = Usuario.objects.get(cedula=request.user.username)

            # ❌ Si ya existe un reporte donde el usuario ya está involucrado con ese bache
            if Reporte.objects.filter(bache=bache, usuario=usuario, involucrado_reporte=True,deleted_at__isnull=True).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Ya reportaste este bache previamente, no necesitas crear una nueva conexion.'
                })

            # ❌ Si ya existe un reporte simple (no involucrado) para ese bache
            if Reporte.objects.filter(bache=bache, involucrado_reporte=False,deleted_at__isnull=True).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Ya reportaste este bache previamente, no necesitas crear una  nueva conexion.'
                })

            # ✅ Crear el reporte simple (no involucrado)
            Reporte.objects.create(bache=bache, usuario=usuario, involucrado_reporte=False)

            return JsonResponse({'success': True})

        except Bache.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Bache no encontrado'})
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt  # si no estás usando CSRF desde JS, puedes usar esto temporalmente
def conectar_bache_admin(request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Cuerpo inválido'}, status=400)

            usuario_raw = data.get('usuario_id')  # Este es el string con nombre (cedula)
            bache_id = data.get('bache_id')

            if not usuario_raw or not bache_id:
                return JsonResponse({'error': 'Falta seleccionar el bache o el usuario.'}, status=400)

            # Extraer la cédula desde el string: 'Angela Gutierrez (0123456789)' -> '0123456789'
            try:
                cedula = usuario_raw.split('(')[-1].strip(')')
            except Exception:
                return JsonResponse({'error': 'Formato de usuario inválido'}, status=400)

            # Buscar el objeto Usuario por cédula
            try:
                usuario = Usuario.objects.get(cedula=cedula)
                bache = Bache.objects.get(id_bache=bache_id)
            except Usuario.DoesNotExist:
                return JsonResponse({'error': 'Usuario no encontrado con esa cédula'}, status=404)
            except Bache.DoesNotExist:
                return JsonResponse({'error': 'Bache no encontrado'}, status=404)

            if usuario.rol == 2:
                return JsonResponse({'error': 'No se puede conectar al administrador'}, status=400)

            # Verificar si ya tiene un reporte con ese bache
            ya_tiene = Reporte.objects.filter(
                usuario=usuario,
                bache=bache,
                involucrado_reporte=False,
                deleted_at__isnull=True
            ).exists()

            if ya_tiene:
                return JsonResponse({'error': 'Ese usuario ya está conectado'}, status=400)

            # Crear reporte
            Reporte.objects.create(usuario=usuario, bache=bache, involucrado_reporte=False)
            return JsonResponse({'success': True})


@login_required
def eliminar_reporte(request, id_reporte):
    if request.method == 'POST':
        try:
            reporte = Reporte.objects.get(pk=id_reporte)
            
            if not reporte.involucrado_reporte:
                # Eliminación física si no está involucrado
                reporte.delete()
                return JsonResponse({'mensaje': 'El reporte fue eliminado correctamente '})
            else:
                # Soft delete si está involucrado
                reporte.deleted_at = now()
                reporte.save()
                return JsonResponse({'mensaje': 'El reporte fue eliminado correctamente'})

        except Reporte.DoesNotExist:
            return JsonResponse({'mensaje': 'El reporte no existe.'}, status=404)

    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)

def consultar_reportes_filtrados(request):
    usuario = Usuario.objects.get(cedula=request.user.username)
    involucrado_param = request.GET.get('involucrado')

    reportes = Reporte.objects.filter(usuario=usuario, deleted_at__isnull=True)

    if involucrado_param == '1':
        reportes = reportes.filter(involucrado_reporte=True)
    elif involucrado_param == '0':
        reportes = reportes.filter(involucrado_reporte=False)

    context = {
        'reportes': reportes,
        'involucrado_param': involucrado_param  # ⬅️ Aquí se lo mandas al template
    }
    return render(request, 'reportes/eliminar_reportes_user.html', context)


@login_required
def consultar_reportes_admin(request):
    try:
        # Obtener los filtros desde GET
        involucrado = request.GET.get('involucrado')  # '1', '0' o None
        usuario_id = request.GET.get('usuario')        # ID del usuario seleccionado
        eliminado = request.GET.get('eliminado')       # 'true', 'false' o None
        involucrado_reporte = request.GET.get('involucrado_reporte')  # 'true', 'false' o None
        id_reporte = request.GET.get('id_report')     # Código del reporte
        baches=request.GET.get('bache_id')

        # Iniciar queryset
        reportes = Reporte.objects.all()

        # Filtro involucrado (MIS REPORTES / MIS CONEXIONES)
        if involucrado == '1':
            reportes = reportes.filter(involucrado_reporte=True)
        elif involucrado == '0':
            reportes = reportes.filter(involucrado_reporte=False)

        # Filtro usuario específico
        if usuario_id:
            try:
                # Extraer la cédula si viene en formato "Nombre Apellido (1234567890)"
                cedula = usuario_id.split('(')[-1].strip(')')
                usuario = Usuario.objects.get(cedula=cedula)
                reportes = reportes.filter(usuario=usuario)
            except (Usuario.DoesNotExist, IndexError):
                # Si falla el formato o el usuario no existe, no filtra por usuario
                pass

        if baches:
            try:
                bache_id = baches.split('(')[-1].strip(')')
                bache = Bache.objects.get(id_bache=bache_id)
                reportes = reportes.filter(bache=bache)
            except (Bache.DoesNotExist, IndexError):
                bache = None  # evita el error si falló la búsqueda

        # Filtro de eliminados
        if eliminado == 'true':
            reportes = reportes.filter(deleted_at__isnull=False)
        elif eliminado == 'false':
            reportes = reportes.filter(deleted_at__isnull=True)

        # Filtro de involucrado en reporte (valor booleano explícito)
        if involucrado_reporte == 'true':
            reportes = reportes.filter(involucrado_reporte=True)
        elif involucrado_reporte == 'false':
            reportes = reportes.filter(involucrado_reporte=False)

        # Filtro por fecha de creación
        fecha_creacion = request.GET.get('created_at')
        if fecha_creacion:
            fecha_obj = parse_date(fecha_creacion)
            if fecha_obj:
                inicio = make_aware(datetime.combine(fecha_obj, datetime.min.time()))
                fin = make_aware(datetime.combine(fecha_obj, datetime.max.time()))
                reportes = reportes.filter(created_at__range=(inicio, fin))
        # Filtro por ID de reporte (si se especifica un código exacto)
        if id_reporte:
            reportes = reportes.filter(id_report__iexact=id_reporte)
        # Obtener lista de usuarios para el filtro en el formulario
        usuarios = Usuario.objects.exclude(rol=2)

        return render(request, 'reportes/consultar_reportes_admin.html', {
            'reportes': reportes,
            'involucrado': involucrado,
            'usuarios': usuarios,
            'baches': bache if 'bache' in locals() else None,
        })

    except Usuario.DoesNotExist:
        return render(request, 'error.html', {
            'mensaje': 'Usuario no encontrado. Asegúrate de que el usuario tenga cédula registrada.'
        })
    
def eliminar_reportes_admin (request):
    try:
        # Obtener los filtros desde GET
        involucrado = request.GET.get('involucrado')  # '1', '0' o None
        usuario_id = request.GET.get('usuario')        # ID del usuario seleccionado
        eliminado = request.GET.get('eliminado')       # 'true', 'false' o None
        involucrado_reporte = request.GET.get('involucrado_reporte')  # 'true', 'false' o None
        id_reporte = request.GET.get('id_report')     # Código del reporte

        # Iniciar queryset
        reportes = Reporte.objects.all()

        # Filtro involucrado (MIS REPORTES / MIS CONEXIONES)
        if involucrado == '1':
            reportes = reportes.filter(involucrado_reporte=True)
        elif involucrado == '0':
            reportes = reportes.filter(involucrado_reporte=False)

        # Filtro usuario específico
        if usuario_id:
            try:
                # Extraer la cédula si viene en formato "Nombre Apellido (1234567890)"
                cedula = usuario_id.split('(')[-1].strip(')')
                usuario = Usuario.objects.get(cedula=cedula)
                reportes = reportes.filter(usuario=usuario)
            except (Usuario.DoesNotExist, IndexError):
                # Si falla el formato o el usuario no existe, no filtra por usuario
                pass
        # Filtro de eliminados
        if eliminado == 'true':
            reportes = reportes.filter(deleted_at__isnull=False)
        elif eliminado == 'false':
            reportes = reportes.filter(deleted_at__isnull=True)

        # Filtro de involucrado en reporte (valor booleano explícito)
        if involucrado_reporte == 'true':
            reportes = reportes.filter(involucrado_reporte=True)
        elif involucrado_reporte == 'false':
            reportes = reportes.filter(involucrado_reporte=False)

        # Filtro por fecha de creación
        fecha_creacion = request.GET.get('created_at')
        if fecha_creacion:
            fecha_obj = parse_date(fecha_creacion)
            if fecha_obj:
                inicio = make_aware(datetime.combine(fecha_obj, datetime.min.time()))
                fin = make_aware(datetime.combine(fecha_obj, datetime.max.time()))
                reportes = reportes.filter(created_at__range=(inicio, fin))
        # Filtro por ID de reporte (si se especifica un código exacto)
        if id_reporte:
            reportes = reportes.filter(id_report__iexact=id_reporte)
        # Obtener lista de usuarios para el filtro en el formulario
        usuarios = Usuario.objects.exclude(rol=2)

        return render(request, 'reportes/eliminar_reportes_admin.html', {
            'reportes': reportes,
            'involucrado': involucrado,
            'usuarios': usuarios,
        })

    except Usuario.DoesNotExist:
        return render(request, 'error.html', {
            'mensaje': 'Usuario no encontrado. Asegúrate de que el usuario tenga cédula registrada.'
        })

@login_required
def eliminar_reporte_definitivo(request, id_reporte):
    try:
        reporte = Reporte.objects.get(id_report=id_reporte)
        reporte.delete()  # Elimina de forma real de la base de datos
        messages.success(request, f'Reporte {id_reporte} eliminado correctamente.')
    except Reporte.DoesNotExist:
        messages.error(request, f'No se encontró el reporte con ID {id_reporte}.')
    
    return redirect('reportes:eliminar_reportes_admin')

@login_required
def gestion_baches_admin(request):
    baches = Bache.objects.all()
    id_bache = request.GET.get('id_bache')
    estado = request.GET.get('estado')
    profundidad = request.GET.get('profundidad')
    tipo_calle = request.GET.get('tipo_calle')
    diametro = request.GET.get('diametro')
    accidentes = request.GET.get('accidentes')
    eliminado = request.GET.get('eliminado')
    fecha_creacion = request.GET.get('fecha_creacion')
    localidad = request.GET.get('localidad')
    upz = request.GET.get('upz')
    barrio = request.GET.get('barrio')

    print("Fecha recibida del filtro:", fecha_creacion)
    if id_bache:
        baches = baches.filter(id_bache__icontains=id_bache)
    if estado:
        baches = baches.filter(estado=estado)
    if profundidad:
        baches = baches.filter(profundidad=profundidad)
    if tipo_calle:
        baches = baches.filter(tipo_calle=tipo_calle)  # corregido: tipo_calle no es ForeignKey
    if diametro:
        baches = baches.filter(diametro__gte=diametro)
    if accidentes:
        baches = baches.filter(accidentes__gte=accidentes)
    if eliminado == 'true':
        baches = baches.filter(deleted_at__isnull=False)
    elif eliminado == 'false':
        baches = baches.filter(deleted_at__isnull=True)
    if fecha_creacion:
        try:
            fecha_inicio = datetime.strptime(fecha_creacion, "%Y-%m-%d")
            fecha_fin = fecha_inicio + timedelta(days=1)
            baches = baches.filter(created_at__range=(fecha_inicio, fecha_fin))
            print("Filtrando entre:", fecha_inicio, "y", fecha_fin)
        except ValueError:
            print("Error en el formato de la fecha")
    if localidad:
        baches = baches.filter(localidad_id=localidad)
    if upz:
        baches = baches.filter(upz_id=upz)
    if barrio:
        baches = baches.filter(barrio_id=barrio)

    # Opciones para el modal o formulario
    profundidad = Profundidad.choices
    estados = Estado.choices
    localidades = Localidad.objects.all()
    upzs = UPZ.objects.all()
    barrios = Barrio.objects.all()
    tipos_calle = Tipo_calle.choices  # corregido: Tipo_calle es TextChoices, no modelo

    return render(request, 'reportes/gestion_baches_admin.html', {
        'baches': baches,
        'estados': estados,
        'localidades': localidades,
        'upzs': upzs,
        'barrios': barrios,
        'tipos_calle': tipos_calle,
        'profundidad': profundidad,
    })



@login_required
@require_POST
@login_required
def eliminar_bache_admin(request, id_bache):
    try:
        print("ID a eliminar:", id_bache)
        bache = get_object_or_404(Bache, id_bache=id_bache)
        bache.delete(hard_delete=True)  # <-- esto está bien
        print("Borrado exitoso")
        return JsonResponse({'mensaje': 'Bache eliminado correctamente'})
    except Exception as e:
        print("Error:", e)
        return JsonResponse({'mensaje': f'Error al eliminar el bache: {str(e)}'}, status=500)