from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views  
urlpatterns = [

    #path('',views.index,name="inicio"),
    path('somos',views.somos,name="somos"),
    path('sesion',views.sesion,name="sesion"),
    path('accesodenegado/',views.denied_access,name='denied_access'),

    #Usuario CRUD
    path('usuario/configuracion',views.configuracion_usuario, name='configuracion_usuario'),
    path('usuario/crear',views.crear_usuario, name='crear_usuario'),
    path('usuario/mostrar/',views.usuario_view, name='usuario'),
    path('usuario/editar//<int:id>',views.editar_usuario, name='editar_usuario'),
    path('usuario/principal/',views.principal_usuario, name='principal_usuario'),
    path('usuario/correo_usuario/',views.actualizar_correo, name='actualizar_correo'),
    path('usuario/recuperar/', views.enviar_codigo_recuperacion, name='enviar_codigo_recuperacion'),         
    path('usuario/confirmar/', views.confirmar_codigo, name='confirmar_codigo'),
    path('usuario/nueva_contrasena/', views.establecer_nueva_contrasena, name='establecer_nueva_contrasena'),
    path('usuario/datos_personales/', views.datos_personales, name='datos_personales'),
    path('usuario/notificacion_usuario/', views.notificaciones_usuario, name='notificacion_usuario'),
    path('usuario/gestionar_cuenta/', views.gestionar_cuenta, name='gestionar_cuenta'),
    path('usuario/PQR/', views.PQR, name='PQR'),
    path('usuario/calificacion/', views.usuario_calificacion, name='calificacion'),
    path('usuario//desactivar_cuenta', views.desactivar_cuenta, name='desactivar_cuenta'),
    path('usuario/verificar-codigo/', views.verificar_codigo_correo, name='verificar_codigo_correo'),
    path('editar_respuesta/', views.editar_respuesta, name='editar_respuesta'),
    path("desactivar-usuario/", views.desactivar_usuario, name="desactivar_usuario"),
    
    path('signup/',views.signup,name='signup'),
    path('logout/',views.signout,name='logout'),
    path('signin/',views.signin,name='signin'),

    #Reporte

    path('reportes/opciones_reportes/', views.opciones_reportes, name='opciones_reportes'),
    path('reportes/consultar_reportes/', views.consultar_reportes, name='consultar_reportes'),
    #admin_
    path('opciones_usuario/', views.opciones_usuario, name='opciones_usuario'),
    path('opciones_bache/', views.opciones_bache, name='opciones_bache'),
    path('opciones_admin/', views.opciones_admin, name='opciones_admin'),
    path('opciones_bache_usuario/', views.opciones_bache_usuario, name='opciones_bache_usuario'),
    path('crear_usuario_admin/', views.crear_usuario_admin, name='crear_usuario_admin'),
    path('gestionar_pqr/', views.gestionar_pqr, name='gestionar_pqr'),
    path('pqr_tramitadas/', views.pqr_tramitadas, name='pqr_tramitadas'),
    path('pqr_consultar/', views.consultar_pqr, name='pqr_consultar'),
    path('usuarios/cambiar_rol/', views.cambiar_rol_usuario, name='cambiar_rol_usuario'),


    re_path(r'^reset/password_reset/$', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html'
    ), name='password_reset'),

    re_path(r'^reset/password_reset_done/$', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
