def rol_usuario(request):
    if request.user.is_authenticated:
        from .models import Usuario  # importa tu modelo real
        try:
            usuario = Usuario.objects.get(cedula=request.user.username)
            return {'rol': usuario.rol}
        except Usuario.DoesNotExist:
            print("Usuario no encontrado")
        except Exception as e:
            print("Error:", e)
    return {'rol': None}