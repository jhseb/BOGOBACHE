from django.urls import path
from . import views
app_name = 'reportes'  # <-- esto es obligatorio para usar 'reportes:crear_reportes'
urlpatterns = [
    path('crear/', views.crear_reportes, name='crear_reportes'),
    path('consultar/', views.consultar_reportes, name='consultar_reportes'),
    path('ver/<str:id_reporte>/', views.ver_reporte_detalle, name='ver_reporte_detalle'),
]