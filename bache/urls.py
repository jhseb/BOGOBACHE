# bache/urls.py

from django.urls import path, include
from . import views
from .views import mapa_baches, upzs_por_localidad, barrios_por_upz, admin_eliminar_bache_directo
from .routers import router
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.ver_filtrado_baches, name='ver_filtrado_baches'),
    path('inicio', views.index, name="inicio"),
    #path('', views.index, name="inicio"),
    path('crear/', views.crear_bache, name='crear_bache'),  # <- Ya no fallará
    #path('somos/', views.somos, name="somos"),
    #path('sesion/', views.sesion, name="sesion"),
    path('mapa/', mapa_baches, name='mapa-baches'),
    path('ajax/baches/', views.listar_baches, name='listar_baches'),
    path('ajax/bache-por-id/<str:id>/', views.obtener_bache_por_id, name='bache_por_id'),

    path('ajax/upzs/', views.cargar_upzs, name='ajax_cargar_upzs'),
    path('ajax/barrios/', views.cargar_barrios, name='ajax_cargar_barrios'),
    path('api/', include(router.urls)),
    path('api/upzs-por-localidad/<int:localidad_id>/', upzs_por_localidad, name='upzs-por-localidad'),
    path('api/barrios-por-upz/<int:upz_id>/', barrios_por_upz, name='barrios-por-upz'),
    path('consultar/', views.ver_filtrado_baches, name='ver_filtrado_baches'),
    path('ajax/filtrar_baches/', views.filtrar_baches, name='filtrar_baches_ajax'),
    path('ajax/obtener_filtros/', views.obtener_filtros, name='obtener_filtros'),

    path('modificar_bache/', views.mostrar_modificar_bache, name='mostrar_modificar_bache'),
    path('modificar_bache/<str:id_bache>/', views.get_bache, name='get_bache'),
    path('modificar_bache/<str:id_bache>/guardar/', views.modificar_bache_post, name='modificar_bache_post'),

    path('registrar-accidente/', views.mostrar_registrar_accidente, name='mostrar_registrar_accidente'),
    path('api/registrar_accidente/<str:id_bache>/', views.api_registrar_accidente, name='api_registrar_accidente'),

    path('eliminar_bache/', views.mostrar_eliminar_bache, name='mostrar_eliminar_bache'),
    path('ajax/buscar_bache_eliminar/', views.buscar_bache_eliminar, name='buscar_bache_eliminar'),
    path('eliminar_bache_confirmar/<str:id>/', views.eliminar_bache_confirmar, name='eliminar_bache_confirmar'),
    path('admin_eliminar_bache_directo/<str:id_bache>/', admin_eliminar_bache_directo, name='admin_eliminar_bache_directo'),

    path('conectar/', views.mostrar_conectar_bache, name='conectar'),
    path('conectar_admin/', views.mostrar_conectar_bache_admin, name='conectar_admin'),
   # path('reportes/', include('reportes.urls')),  #esta línea no puede servir para mostrar el formulario
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
