from django.shortcuts import render, redirect
from .models import  Usuario
from reportes.models import Reporte
from django.core.mail import send_mail
from .form import usuarioForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import IntegrityError
from django.contrib.auth.models import Group
from django.contrib.auth import login,logout, authenticate
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random
from django.contrib import messages
from .models import Servicio
from usuario.models import Usuario
from django.core.exceptions import MultipleObjectsReturned
from django.utils.timezone import localtime
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
# Create your views here.
def index(request):
    #return HttpResponse("HOLA")
    title = 'PAGINA'
    return render(request,'visitante/index.html',{ 'title':title})


def somos(request):
    #return HttpResponse("HOLA")
    title = 'PAGINA'
    return render(request,'visitante/somos.html',{ 'title':title})

def sesion(request):
    #return HttpResponse("HOLA")
    title = 'PAGINA'
    return render(request,'visitante/sesion.html',{ 'title':title})


def restringir(request, username):
    nombre_grupo = 'admin'
    nombre_grupo1 = 'usuario'
    rol =(Usuario.objects.get(cedula=username)).rol
    grupo = Group.objects.filter(name=nombre_grupo).first()
    # Verificar si el grupo 'usuario' existe
    grupo1 = Group.objects.filter(name=nombre_grupo1).first()
    if not grupo:
        grupo = Group.objects.create(name=nombre_grupo)  
        print(f'El grupo "{nombre_grupo}" ha sido creado.')
    else:
        print(f'El grupo "{nombre_grupo}" ya existe.')
    
    if not grupo1:
        grupo1 = Group.objects.create(name=nombre_grupo1)  
        print(f'El grupo "{nombre_grupo1}" ha sido creado.')
    else:
        print(f'El grupo "{nombre_grupo1}" ya existe.')

    try:
        usuario = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f'El usuario con nombre de usuario "{username}" no existe.')
        return

    if rol == 2 :
        usuario.groups.add(grupo)
    
    else:
        usuario.groups.add(grupo1)   

def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_usuario(user):
    return user.groups.filter(name='usuario').exists()

def denied_access(request):
    return HttpResponse("Acceso denegado", status=403)

#CRUD DE USUARIOS

def obtener_usuario(request):
    if request.user.is_authenticated:
        username = request.user.username
        usu = Usuario.objects.get(cedula=username)
        return usu
    return None  # Si el usuario no está autenticado, retorna None

def crear_usuario(request):
    #cliente0 = obtener_usuario(request)
    formulario = usuarioForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('usuario')
    return render(request, 'usuario/crear.html',{'formulario': formulario})

#@user_passes_test(is_usuario, login_url='denied_access')
@user_passes_test(is_admin, login_url='denied_access')  
def usuario_view(request):
    #cliente0 = obtener_usuario(request)
    usuarios = Usuario.objects.all()
    return render(request, 'usuario/index.html',{'usuarios':usuarios})


def editar_usuario(request, id):
    usuario1 = get_object_or_404(Usuario, cedula=id)
    formulario = usuarioForm(request.POST or None, request.FILES or None, instance=usuario1)

    grupo_admin = Group.objects.filter(name='admin').first()
    grupo_usuario = Group.objects.filter(name='usuario').first()

    estado = None  # 'exito' o 'error'

    if request.method == 'POST':
        if formulario.is_valid():
            formulario.save()

            userb = User.objects.get(username=usuario1.cedula)
            userb.email = formulario.cleaned_data['email']
            userb.groups.clear()

            if formulario.cleaned_data['rol'] == 1:
                userb.groups.add(grupo_usuario)
            else:
                userb.groups.add(grupo_admin)

            userb.username = formulario.cleaned_data['cedula']
            userb.save()

            estado = 'exito'
        else:
            estado = 'error'

    return render(request, 'usuario/editar.html', {
        'formulario': formulario,
        'estado': estado
    })



def enviar_correo_usuario(user):
    if isinstance(user, User):
        destinatario = user.email
        nombre_usuario = Usuario.objects.get(cedula=user.username).nombre

    else:
        raise ValueError("El parámetro debe ser una instancia del modelo User.")

    asunto = 'Bienvenido a nuestra BOGOBACHE'
    mensaje = f'Hola {nombre_usuario}, se te quiere informar que la cuenta ya fue creada.'
    remitente = 'bogobacheteam@gmail.com'

    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=remitente,
        recipient_list=[destinatario],
        fail_silently=False,
    )

def caso_usuario_3(cedula, request):
    try:
        usuario = Usuario.objects.get(cedula=cedula)
    except Usuario.DoesNotExist:
        return  # O manejar el caso de error según necesites

    usuario.nombre = request.POST['nombre']
    usuario.apellido = request.POST['apellido']
    usuario.fecha_nacimiento = request.POST['fecha_nacimiento']
    usuario.localidad = request.POST['localidad']
    usuario.medio_trans = request.POST['medio_trans']

    if request.POST['email'] == usuario.email:
        if request.POST['password1'] != request.POST['password2']:
            usuario.email = request.POST['email']
            usuario.notificacion = bool(request.POST.get('notificacion'))
            usuario.rol = 1  # Si deseas forzar siempre rol=1
            usuario.save()
            user = User.objects.get(username=cedula)
            user.email = request.POST['email']
            user.password = request.POST['password1']
            user.save()
            login(request, user)
            return redirect('principal_usuario')
    else:
        correo_existe = Usuario.objects.filter(email=request.POST['email']).exists()
        if not correo_existe:
            if request.POST['password1'] != request.POST['password2']:
                usuario.email = request.POST['email']
                usuario.notificacion = bool(request.POST.get('notificacion'))
                usuario.rol = 1  # Si deseas forzar siempre rol=1
                usuario.save()
                user = User.objects.get(username=cedula)
                user.email = request.POST['email']
                user.password = request.POST['password1']
                user.save()
                login(request, user)
                return redirect('principal_usuario')
        
            

def signup(request):
    if request.method == 'GET':
        return render(request, 'usuario/signup.html', {'form': UserCreationForm})
    else:
        cedula = request.POST['cedula']

        try:
            user_rol = Usuario.objects.get(cedula=cedula).rol
            if user_rol == 3:
                try:
                    usuario = Usuario.objects.get(cedula=cedula)
                except Usuario.DoesNotExist:
                    return  # O manejar el caso de error según necesites

                usuario.nombre = request.POST['nombre']
                usuario.apellido = request.POST['apellido']
                usuario.fecha_nacimiento = request.POST['fecha_nacimiento']
                usuario.localidad = request.POST['localidad']
                usuario.medio_trans = request.POST['medio_trans']

                if request.POST['email'] == usuario.email:
                    if request.POST['password1'] == request.POST['password2']:
                        usuario.email = request.POST['email']
                        usuario.nombre = request.POST['nombre']
                        usuario.apellido = request.POST['apellido']
                        usuario.fecha_nacimiento = request.POST['fecha_nacimiento']
                        usuario.notificacion = bool(request.POST.get('notificacion'))
                        usuario.rol = 1  # Si deseas forzar siempre rol=1
                        usuario.ciudad_origen = request.POST['ciudad']
                        usuario.telefono = request.POST['telefono']
                        usuario.medio_trans=request.POST['medio_trans'],
                        usuario.save()
                        user = User.objects.get(username=cedula)
                        user.email = request.POST['email']
                        user.set_password(request.POST['password1'])
                        user.save()
                        login(request, user)
                        return redirect('principal_usuario')
                else:
                    correo_existe = Usuario.objects.filter(email=request.POST['email']).exists()
                    if not correo_existe:
                        if request.POST['password1'] == request.POST['password2']:
                            usuario.email = request.POST['email']
                            usuario.nombre = request.POST['nombre']
                            usuario.apellido = request.POST['apellido']
                            usuario.fecha_nacimiento = request.POST['fecha_nacimiento']
                            usuario.notificacion = bool(request.POST.get('notificacion'))
                            usuario.rol = 1  # Si deseas forzar siempre rol=1
                            usuario.ciudad_origen = request.POST['ciudad']
                            usuario.telefono = request.POST['telefono']
                            usuario.medio_trans=request.POST['medio_trans'],
                            usuario.save()
                            user = User.objects.get(username=cedula)
                            user.email = request.POST['email']
                            user.set_password(request.POST['password1'])
                            user.save()
                            login(request, user)
                            return redirect('principal_usuario')  
        except Usuario.DoesNotExist:
            pass  # Si no existe el usuario, continúa normalmente

        correo = request.POST['email']
        cedula_existe = Usuario.objects.filter(cedula=cedula).exists()
        correo_existe = Usuario.objects.filter(email=correo).exists()

        if cedula_existe or correo_existe:
            return render(request, 'usuario/signup.html', {
                'form': UserCreationForm,
                'error': 'La cédula o el correo ya están registrados o contraseña incorrecta'
            })

        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['cedula'],
                    password=request.POST['password1'],
                    email=request.POST['email']
                )

                usuario = Usuario.objects.create(
                    cedula=cedula,
                    nombre=request.POST['nombre'],
                    apellido=request.POST['apellido'],
                    fecha_nacimiento=request.POST['fecha_nacimiento'],
                    localidad=request.POST['localidad'],
                    medio_trans=request.POST['medio_trans'],
                    email=request.POST['email'],
                    ciudad_origen = request.POST['ciudad'],
                    telefono = request.POST['telefono'],
                    notificacion=bool(request.POST.get('notificacion')),
                    rol=1
                )

                user.save()
                enviar_correo_usuario(user)
                restringir(request, cedula)
                login(request, user)

                if usuario.rol == 2:
                    return redirect('somos')
                else:
                    return redirect('principal_usuario')

            except IntegrityError:
                return render(request, 'usuario/signup.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                })

        return render(request, 'usuario/signup.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })


def signin(request):
    if request.method == 'GET':
        return render(request, 'visitante/sesion.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'visitante/sesion.html', {
                'form': AuthenticationForm,
                'error': 'Contraseña incorrecta o usuario inexistente'
            })
        else:
            try:
                usu = Usuario.objects.get(cedula=request.POST['username']).rol
            except Usuario.DoesNotExist:
                return render(request, 'visitante/sesion.html', {
                    'form': AuthenticationForm,
                    'error': 'Usuario no registrado en el sistema'
                })

            if usu == 3:
                return render(request, 'visitante/sesion.html', {
                    'form': AuthenticationForm,
                    'error': 'Usuario no registrado en el sistema'
                })

            login(request, user)

            if usu == 2:
                return redirect('opciones_admin')
            else:
                return redirect('principal_usuario')

            
def signout(request):
    logout(request)
    return redirect('signin')


def configuracion_usuario(request):
    title = 'PÁGINA'
    return render(request, 'usuario/configuracion.html', {'title': title})

#admin

def opciones_usuario(request):
    title = 'PÁGINA'
    return render(request, 'administrador/opciones_usuario.html', {'title': title})

def opciones_bache(request):
    title = 'PÁGINA'
    return render(request, 'administrador/opciones_bache.html', {'title': title})

def opciones_admin(request):
    title = 'PÁGINA'
    return render(request, 'administrador/base_admin.html', {'title': title})

def principal_usuario(request):
    title = 'PÁGINA'
    return render(request, 'usuario/principal_usuario.html', {'title': title})


def opciones_reportes(request):
    title = 'PÁGINA'
    return render(request, 'reportes/opciones_reportes.html', {'title': title})

def opciones_bache_usuario(request):
    title = 'PÁGINA'
    return render(request, 'administrador/opciones_bache_usuario.html', {'title': title})


def consultar_reportes(request):
    title = 'PÁGINA'
    return render(request, 'reportes/consultar_reportes.html', {'title': title})



def actualizar_correo(request):
    title = 'PÁGINA'
    usuario = obtener_usuario(request)

    if not usuario:
        return render(request, 'usuario/actualizar_correo.html', {
            'error': 'Usuario no encontrado',
            'correo_actual': '',
            'title': title
        })

    if request.method == 'POST':
        nuevo_correo = request.POST.get('nuevo_correo')
        nuevo_correo2 = request.POST.get('nuevo_correo2')

        if nuevo_correo and nuevo_correo2:
            if nuevo_correo == nuevo_correo2:
                # Validar si ya existe en otro usuario
                if Usuario.objects.filter(email=nuevo_correo).exclude(cedula=usuario.cedula).exists():
                    return render(request, 'usuario/actualizar_correo.html', {
                        'error': 'Este correo ya está registrado por otro usuario.',
                        'correo_actual': usuario.email,
                        'title': title
                    })

                # Generar código de verificación
                codigo = random.randint(100000, 999999)

                # Guardar temporalmente en sesión
                request.session['codigo_verificacion'] = str(codigo)
                request.session['nuevo_correo'] = nuevo_correo

                # Enviar correo con código
                send_mail(
                    'Código de verificación',
                    f'Tu código de verificación es: {codigo}',
                    'no-responder@miapp.com',  # Cambia por el remitente real
                    [nuevo_correo],
                    fail_silently=False,
                )

                return redirect('verificar_codigo_correo')
            else:
                return render(request, 'usuario/actualizar_correo.html', {
                    'error': 'Los correos ingresados no coinciden.',
                    'correo_actual': usuario.email,
                    'title': title
                })
        else:
            return render(request, 'usuario/actualizar_correo.html', {
                'error': 'Debe ingresar ambos correos.',
                'correo_actual': usuario.email,
                'title': title
            })

    return render(request, 'usuario/actualizar_correo.html', {
        'title': title,
        'correo_actual': usuario.email
    })



def verificar_codigo_correo(request):
    title = 'PÁGINA'
    usuario = obtener_usuario(request)

    if not usuario:
        return redirect('actualizar_correo')

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        codigo_enviado = request.session.get('codigo_verificacion')
        nuevo_correo = request.session.get('nuevo_correo')

        if codigo_ingresado == codigo_enviado and nuevo_correo:
            # Actualiza el correo en el modelo Usuario
            usuario.email = nuevo_correo
            usuario.save()

            user = User.objects.get(username=usuario.cedula)
            user.email = nuevo_correo
            user.save()

            # Limpia sesión
            request.session.pop('codigo_verificacion', None)
            request.session.pop('nuevo_correo', None)

            return render(request, 'usuario/verificar_codigo.html', {
                'correo_actualizado': True,
                'title': title
            })

        else:
            return render(request, 'usuario/verificar_codigo.html', {
                'error': 'Código incorrecto.',
                'title': title
            })

    return render(request, 'usuario/verificar_codigo.html', {
        'title': title
    })



@user_passes_test(is_admin, login_url='denied_access') 
def crear_usuario_admin(request):
    if request.method == 'GET':
        return render(request, 'usuario/crear_usuario_admin.html', {'form': UserCreationForm})
    else:
        cedula = request.POST['cedula']
        correo = request.POST['email']

        cedula_existe = Usuario.objects.filter(cedula=cedula).exists()
        correo_existe = Usuario.objects.filter(email=correo).exists()

        if cedula_existe or correo_existe:
            return render(request, 'usuario/crear_usuario_admin.html', {
                'form': UserCreationForm,
                'error': 'La cédula o el correo ya están registrados'
            })

        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['cedula'],
                    password=request.POST['password1'],
                    email=request.POST['email']
                )

                usuario = Usuario.objects.create(
                    cedula=cedula,
                    nombre=request.POST['nombre'],
                    apellido=request.POST['apellido'],
                    fecha_nacimiento=request.POST['fecha_nacimiento'],
                    localidad=request.POST['localidad'],
                    medio_trans=request.POST['medio_trans'],
                    email=request.POST['email'],
                    notificacion=bool(request.POST.get('notificacion')),
                    ciudad_origen = request.POST['ciudad'],
                    telefono = request.POST['telefono'],
                    rol=request.POST['rol'], 
                )

                user.save()
                enviar_correo_usuario(user)
                restringir(request, cedula)
                login(request, user)

                return redirect('usuario')

            except IntegrityError:
                return render(request, 'usuario/crear_usuario_admin.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                })

        return render(request, 'usuario/crear_usuario_admin.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })


def enviar_codigo_recuperacion(request):
    if request.method == 'POST':
        email = request.user.email  
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'usuario//usuario_contraseña/enviar_codigo.html', {
                'error': 'No se encontró el usuario.'
            })
        except MultipleObjectsReturned:
            return render(request, 'usuario//usuario_contraseña/enviar_codigo.html', {
                'error': 'Se encontraron múltiples usuarios con este correo. Contacta soporte.'
            })

        # Si todo está bien, continuar
        codigo = str(random.randint(100000, 999999))

        request.session['codigo_recuperacion'] = codigo
        request.session['codigo_usuario_id'] = user.id
        request.session['codigo_expiracion'] = timezone.now().timestamp() + 300  # 5 minutos

        # Enviar correo
        send_mail(
            'Código de recuperación de contraseña',
            f'Tu código es: {codigo}',
            'no-reply@tuapp.com',
            [email],
            fail_silently=False,
        )

        return redirect('confirmar_codigo')

    return render(request, 'usuario//usuario_contraseña/enviar_codigo.html')


def confirmar_codigo(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')

        codigo_guardado = request.session.get('codigo_recuperacion')
        usuario_id = request.session.get('codigo_usuario_id')
        expiracion = request.session.get('codigo_expiracion')

        if not codigo_guardado or not usuario_id:
            return render(request, 'usuario//usuario_contraseña/confirmar_codigo.html', {'error': 'No se ha solicitado recuperación.'})

        if timezone.now().timestamp() > expiracion:
            return render(request, 'usuario//usuario_contraseña/confirmar_codigo.html', {'error': 'El código ha expirado.'})

        if codigo_ingresado != codigo_guardado:
            return render(request, 'usuario//usuario_contraseña/confirmar_codigo.html', {'error': 'Código incorrecto.'})

        # Código correcto -> marcar como verificado en sesión
        request.session['codigo_verificado'] = True

        return redirect('establecer_nueva_contrasena')

    return render(request, 'usuario//usuario_contraseña/confirmar_codigo.html')


def establecer_nueva_contrasena(request):
    if not request.session.get('codigo_verificado'):
        return redirect('enviar_codigo_recuperacion')

    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        usuario_id = request.session.get('codigo_usuario_id')

        if nueva_contrasena != confirmar_contrasena:
            return render(request, 'usuario//usuario_contraseña/nueva_contrasena.html', {'error': 'Las contraseñas no coinciden.'})

        try:
            user = User.objects.get(id=usuario_id)
            user.set_password(nueva_contrasena)
            user.save()

            request.session.flush()  # Limpiar sesión

            # Mostrar alerta directamente
            return render(request, 'usuario//usuario_contraseña/nueva_contrasena.html', {'success': True})

        except User.DoesNotExist:
            return render(request, 'usuario//usuario_contraseña/nueva_contrasena.html', {'error': 'Usuario no encontrado.'})

    return render(request, 'usuario/usuario_contraseña/nueva_contrasena.html')


def datos_personales(request):
    usuario1 = Usuario.objects.get(cedula=request.user.username)
    formulario = usuarioForm(request.POST or None, request.FILES or None, instance=usuario1)
    nombre_grupo = 'admin'
    nombre_grupo1 = 'usuario'
    grupo = Group.objects.filter(name=nombre_grupo).first()
    grupo1 = Group.objects.filter(name=nombre_grupo1).first()

    if formulario.is_valid() and  request.POST:
        formulario.save()
        userb = User.objects.get(username=usuario1.cedula)
        userb.email = formulario.cleaned_data['email']
        userb.groups.clear()   
        if formulario.cleaned_data['rol'] == 1:
            userb.groups.add(grupo1)
        else:
            userb.groups.add(grupo)

        userb.username = formulario.cleaned_data['cedula']
        userb.save()

        return redirect('configuracion_usuario')
    print("hola")
    return render(request,'usuario/datos_personales.html',{'formulario': formulario})


def notificaciones_usuario(request):
    usuario = obtener_usuario(request)

    if request.method == 'POST':
        # Obtener el valor del checkbox: existe solo si está activado
        notificaciones_activadas = request.POST.get('notificaciones') == 'on'
        usuario.notificacion = notificaciones_activadas
        usuario.save()

    return render(request, 'usuario/notificacion_usuario.html', {
        'usuario': usuario
    })

def gestionar_cuenta(request):
    usuario = obtener_usuario(request)
   
    return render(request, 'usuario/gestion_cuenta.html', {
            'error': 'Usuario no encontrado'
    })  

def PQR(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        comentario = request.POST.get('comentario')

        usuario = request.user

        try:
            usuario_obj = Usuario.objects.get(cedula=usuario.username)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('PQR')

        # Prefijo según tipo
        prefijo = {
            'Queja': 'QJ',
            'Petición': 'PT',
            'Reclamo': 'RC'
        }.get(tipo, 'XX')

        contador = Servicio.objects.filter(tipo=tipo).count() + 1
        id_request = f"{prefijo}-{contador}"

        Servicio.objects.create(
            id_request=id_request,
            cedula=usuario_obj,
            tipo=tipo,
            valor=0,
            comentario=comentario,
            respuesta='',
            fecha_solicitud=timezone.localtime(),  
            estado="Por tramitar"
        )

        return redirect(f'/usuario/PQR/?enviado={tipo}')

    enviado = request.GET.get('enviado', None)
    return render(request, 'usuario/gestion_cuenta/PQR.html', {
        'title': 'PQR',
        'enviado': enviado
    })


def usuario_calificacion(request):
    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario')
        usuario = request.user

        try:
            usuario_obj = Usuario.objects.get(cedula=usuario.username)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('PQR')

        # Contar registros existentes tipo calificacion
        total = Servicio.objects.filter(tipo='calificacion').count() + 1
        id_personalizado = f"CALIFI-{total}"

        # Crear el registro en Servicio
        Servicio.objects.create(
            id_request=id_personalizado,
            cedula=usuario_obj,
            tipo='calificacion',
            valor=int(puntuacion),
            respuesta="",
            comentario=comentario,
            fecha_solicitud=timezone.localtime(), 
            estado="Calificacion"
        )

        messages.success(request, 'Gracias por tu calificación.')
        return redirect('calificacion')

    return render(request, 'usuario/gestion_cuenta/calificacion.html', {
        'title': 'Calificación del Servicio'
    })


def desactivar_cuenta(request):
    usuario = obtener_usuario(request)
    if request.method == 'POST':
        usuario.rol = 3
        usuario.save()  # Guarda el cambio en la base de datos
        return redirect('sesion')  # Redirige tras desactivar (ajusta según tu proyecto)

    return render(request, 'usuario/gestion_cuenta/desactivar_cuenta.html', {
        'usuario': usuario,
    })

def gestionar_pqr(request):
    servicios = Servicio.objects.filter(estado='Por tramitar')
    return render(request, 'administrador/gestionar_pqr.html', {'servicios': servicios})

def consultar_pqr(request):
    filtro = request.GET.get('filtro')
    cedula_usuario = request.user.username

    if filtro == 'pqr':
        servicios = Servicio.objects.filter(cedula=cedula_usuario, estado__in=['Solucionada', 'Por tramitar'])
    elif filtro == 'calificacion':
        servicios = Servicio.objects.filter(cedula=cedula_usuario, estado='Calificacion')
    else:
        servicios = Servicio.objects.filter(cedula=cedula_usuario)

    return render(request, 'usuario/consultar_pqr_cal.html', {'servicios': servicios})




def editar_respuesta(request):
    if request.method == 'POST':
        id_request = request.POST.get('id_request')
        nueva_respuesta = request.POST.get('nueva_respuesta')

        try:
            servicio = Servicio.objects.select_related('cedula').get(id_request=id_request)

            # Guardar nueva respuesta
            servicio.respuesta = nueva_respuesta
            servicio.estado = "Solucionada"
            servicio.save()

            # Verificar que el usuario tenga correo
            destinatario = servicio.cedula.email
            if not destinatario:
                return JsonResponse({'success': False, 'error': 'El usuario no tiene correo registrado.'})

            # Formatear fecha para mostrar solo día, mes y año
            fecha_formateada = servicio.fecha_solicitud.strftime('%Y-%m-%d')  # Puedes cambiar el formato si deseas

            # Preparar mensaje
            asunto = f"Respuesta a su {servicio.tipo}"
            mensaje = f"""
Hola,

Se ha respondido su solicitud con la siguiente información:

ID de solicitud: {servicio.id_request}
Tipo: {servicio.tipo}
Fecha: {fecha_formateada}
Que tenga un buen día señor(a): {servicio.cedula}
Recibimos una solicitud para:
{servicio.comentario}

Respuesta:
{servicio.respuesta}
"""

            # Enviar correo
            send_mail(
                asunto,
                mensaje,
                'tu_correo@dominio.com',  # Reemplaza con el correo de tu sistema
                [destinatario],
                fail_silently=False,
            )

            return JsonResponse({'success': True})

        except Servicio.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Solicitud no encontrada.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})



def pqr_tramitadas(request):
    filtro = request.GET.get('filtro')

    if filtro == 'pqr':
        servicios = Servicio.objects.filter(estado='Solucionada')
    elif filtro == 'calificacion':
        servicios = Servicio.objects.filter(estado='Calificacion')
    else:
        servicios = Servicio.objects.none()  # o puedes mostrar todos si prefieres

    return render(request, 'administrador/pqr_tramitadas.html', {'servicios': servicios})



@csrf_exempt
def cambiar_rol_usuario(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        nuevo_rol = request.POST.get('rol')  # "1", "2", "3"

        try:
            user = User.objects.get(username=cedula)
            usuario = Usuario.objects.get(cedula=cedula)
            usuario.rol = nuevo_rol
            usuario.save()

            # Solo modificamos grupos si es "1" o "2"
            if nuevo_rol == "2":
                user.groups.clear()
                grupo = Group.objects.get(name="admin")
                user.groups.add(grupo)
                user.is_active = True
                user.save()

            elif nuevo_rol == "1":
                user.groups.clear()
                grupo = Group.objects.get(name="usuario")
                user.groups.add(grupo)
                user.is_active = True
                user.save()

            # Si es "3", no se hace nada en el objeto User
            return JsonResponse({'status': 'success'})

        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


def desactivar_usuario(request):
    if request.method == "POST":
        cedula = request.POST.get("cedula")
        try:
            usuario = Usuario.objects.get(cedula=cedula)
            usuario.rol = "3"  # Cambia solo el rol
            usuario.save()
            return JsonResponse({'status': 'success'})
        except Usuario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

def opciones_reportes_admin(request):
    title = 'PÁGINA'
    return render(request, 'reportes/opciones_reportes_admin.html', {'title': title})


def analisis_de_datos(request):
    title = 'PÁGINA'
    return render(request, 'analisis_de_datos/datos.html', {'title': title})


def datos_tipo_vehiculo(request):
    data = (
        Reporte.objects.values('tipo_vehiculo')
        .annotate(total=Count('tipo_vehiculo'))
        .order_by('-total')
    )
    labels = [d['tipo_vehiculo'] for d in data]
    valores = [d['total'] for d in data]
    return JsonResponse({'labels': labels, 'data': valores})