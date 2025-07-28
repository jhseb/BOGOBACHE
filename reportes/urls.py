from django.urls import path
from . import views
app_name = 'reportes'  # <-- esto es obligatorio para usar 'reportes:crear_reportes'
urlpatterns = [
    path('crear/', views.crear_reportes, name='crear_reportes'),
    path('consultar/', views.consultar_reportes, name='consultar_reportes'),
    path('ver/<str:id_reporte>/', views.ver_reporte_detalle, name='ver_reporte_detalle'),
    path('crear_simple/', views.crear_reporte_simple, name='crear_reporte_simple'),
    path('ajax/conectar_bache_admin/', views.conectar_bache_admin, name='conectar_bache_admin'),
    path('consultar_filtrados/', views.consultar_reportes_filtrados, name='consultar_reportes_filtrados'),
    path('eliminar/<str:id_reporte>/', views.eliminar_reporte, name='eliminar_reporte'),
    path('consultar_admin/', views.consultar_reportes_admin, name='consultar_reportes_admin'),
    path('eliminar_admin/', views.eliminar_reportes_admin, name='eliminar_reportes_admin'),
    path('eliminar_reporte_definitivo/<str:id_reporte>/', views.eliminar_reporte_definitivo, name='eliminar_reporte_definitivo'),
    path('detalle_admin/<str:id_reporte>/', views.ver_reporte_detalle_admin, name='ver_reporte_detalle_admin'),
    path('consultar_baches_admin/', views.gestion_baches_admin, name='gestion_baches_admin'),
    path('eliminar_bache_admin/<str:id_bache>/', views.eliminar_bache_admin, name='eliminar_bache_admin'),
]