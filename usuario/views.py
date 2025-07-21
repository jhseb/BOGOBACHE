from django.shortcuts import render, redirect
from .models import  Usuario
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


def usuario_view(request):
    #cliente0 = obtener_usuario(request)
    usuarios = Usuario.objects.all()
    return render(request, 'usuario/index.html',{'usuarios':usuarios})



def editar_usuario(request, id):

    usuario1 = Usuario.objects.get(cedula=id)
    formulario = usuarioForm(request.POST or None, request.FILES or None, instance=usuario1)
    nombre_grupo = 'admin'
    nombre_grupo1 = 'usuario'
    grupo = Group.objects.filter(name=nombre_grupo).first()
    grupo1 = Group.objects.filter(name=nombre_grupo1).first()

    if formulario.is_valid() and  request.POST:
        formulario.save()
        userb = User.objects.get(username=formulario.cleaned_data['cedula'])
        userb.groups.clear()   
        if formulario.cleaned_data['rol'] == 1:
            userb.groups.add(grupo1)
        else:
            userb.groups.add(grupo)

        return redirect('usuario')
    return render(request,'usuario/editar.html',{'formulario': formulario})



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





def signup(request):
    if request.method == 'GET':
        return render(request, 'usuario/signup.html', {'form': UserCreationForm})
    else:
        cedula = request.POST['cedula']
        correo = request.POST['email']

        cedula_existe = Usuario.objects.filter(cedula=cedula).exists()
        correo_existe = Usuario.objects.filter(email=correo).exists()

        if cedula_existe or correo_existe:
            return render(request, 'usuario/signup.html', {
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
    if request.method=='GET':
        return render(request,'visitante/sesion.html',{ 'form': AuthenticationForm})
    else:
        user = authenticate(request,username=request.POST['username'], password=request.POST['password'])
        if user is None:
             return render(request,'visitante/sesion.html',{ 'form': AuthenticationForm,'error':'Contraseña incorrecta o usuario inexistente'})
        else:
            usu=(Usuario.objects.get(cedula=(request.POST['username']))).rol
            login(request,user)
            print(usu)
            if usu == 2 :
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

from django.urls import reverse
from django.http import HttpResponseRedirect

from django.urls import reverse
from django.shortcuts import redirect

def actualizar_correo(request):
    title = 'PÁGINA'
    usuario = obtener_usuario(request)

    if request.method == 'POST':
        nuevo_correo = request.POST.get('nuevo_correo')
        nuevo_correo2 = request.POST.get('nuevo_correo2')

        if nuevo_correo and nuevo_correo2 and nuevo_correo == nuevo_correo2:
            if usuario:
                usuario.email = nuevo_correo
                usuario.save()
                # Redirige con el parámetro GET (para mostrar la alerta)
                return redirect(reverse('actualizar_correo') + '?actualizado=1')
            else:
                return render(request, 'usuario/actualizar_correo.html', {
                    'error': 'Usuario no encontrado',
                    'correo_actual': '',
                    'title': title
                })
        else:
            return render(request, 'usuario/actualizar_correo.html', {
                'error': 'Los correos no coinciden',
                'correo_actual': usuario.email if usuario else '',
                'title': title
            })

    # Si es GET y se actualizó correctamente, muestra el mensaje
    mensaje = None
    if request.GET.get('actualizado') == '1':
        mensaje = 'Correo actualizado correctamente.'

    return render(request, 'usuario/actualizar_correo.html', {
        'title': title,
        'correo_actual': usuario.email if usuario else '',
        'mensaje': mensaje
    })



