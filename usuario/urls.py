from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views  
urlpatterns = [

    #path('',views.index,name="inicio"),
    path('somos',views.somos,name="somos"),
    path('sesion',views.sesion,name="sesion"),


    #Usuario CRUD
    path('usuario/configuracion',views.configuracion_usuario, name='configuracion_usuario'),
    path('usuario/crear',views.crear_usuario, name='crear_usuario'),
    path('usuario/mostrar/',views.usuario_view, name='usuario'),
    path('usuario/editar//<int:id>',views.editar_usuario, name='editar_usuario'),
    path('usuario/principal/',views.principal_usuario, name='principal_usuario'),

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
