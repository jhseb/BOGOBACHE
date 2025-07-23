from django.urls import path
from . import views

urlpatterns = [
    path('consultar/', views.consultar_reportes, name='consultar_reportes'),
]