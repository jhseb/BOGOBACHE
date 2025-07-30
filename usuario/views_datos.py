from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, connection
from django.utils import timezone
from django.utils.timezone import localtime
from io import BytesIO

# Formularios
from .form import usuarioForm

# Modelos
from .models import Usuario, Servicio
from reportes.models import Reporte
from bache.models import Bache, Tipo_calle, Localidad

# Librerías para gráficos
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter, defaultdict
from django.db.models import Avg
from datetime import datetime
import random
import locale
import calendar


def servicios_mas_y_menos(servicio_filtro=''):
    servicios = {
        'aseguradora': ('Aseguradora', 'servicio_aseguradora'),
        'abogados': ('Abogados', 'servicio_abogados'),
        'bomberos': ('Bomberos', 'servicio_bomberos'),
        'medicos': ('Médicos', 'servicio_medicos')
    }

    # 🔹 Filtramos la tabla solo con registros involucrados
    base_qs = Reporte.objects.filter(involucrado_reporte=1)

    nombres = []
    conteos = []

    for clave, (nombre, campo) in servicios.items():
        if not servicio_filtro or servicio_filtro == clave:
            count = base_qs.filter(**{f"{campo}__in": ['bueno', 'excelente']}).count()
            nombres.append(nombre)
            conteos.append(count)

    if not nombres:
        nombres = ['Sin datos']
        conteos = [0]

    plt.figure(figsize=(8, 5))
    barras = plt.bar(nombres, conteos, color=['#007bff', '#28a745', '#ffc107', '#dc3545'][:len(nombres)])
    plt.title('Servicios mejor calificados')
    plt.xlabel('Servicio')
    plt.ylabel('Cantidad de calificaciones buenas o excelentes')
    plt.ylim(0, max(conteos) + 1 if max(conteos) > 0 else 1)

    for bar in barras:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, int(yval), ha='center', va='bottom')

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return imagen_base64

def servicios_peor_calificados(servicio_filtro=''):
    servicios = {
        'aseguradora': ('Aseguradora', 'servicio_aseguradora'),
        'abogados': ('Abogados', 'servicio_abogados'),
        'bomberos': ('Bomberos', 'servicio_bomberos'),
        'medicos': ('Médicos', 'servicio_medicos')
    }

    # 🔹 Filtramos la tabla base solo con registros involucrados
    base_qs = Reporte.objects.filter(involucrado_reporte=1)

    nombres = []
    conteos = []

    for clave, (nombre, campo) in servicios.items():
        if not servicio_filtro or servicio_filtro == clave:
            # 🔹 Solo contamos los que tienen calificación muy deficiente o deficiente
            count = base_qs.filter(**{f"{campo}__in": ['muy deficiente', 'deficiente']}).count()
            nombres.append(nombre)
            conteos.append(count)

    if not nombres:
        nombres = ['Sin datos']
        conteos = [0]

    plt.figure(figsize=(8, 5))
    barras = plt.bar(nombres, conteos, color=['#ff5733', '#c70039', '#900c3f', '#581845'][:len(nombres)])
    plt.title('Servicios peor calificados')
    plt.xlabel('Servicio')
    plt.ylabel('Cantidad de calificaciones muy deficientes o deficientes')
    plt.ylim(0, max(conteos) + 1 if max(conteos) > 0 else 1)

    for bar in barras:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, int(yval), ha='center', va='bottom')

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return imagen_base64


def contar_reportes():
    return Reporte.objects.filter(involucrado_reporte=1).count()


def grafico_dias_con_mas_reportes(dia=None):
    # 🔹 Filtrar solo los registros involucrados
    reportes = Reporte.objects.filter(involucrado_reporte=1)

    # 🔹 Si se pasa un día específico, filtrarlo también
    if dia:
        reportes = reportes.filter(dia_evento__iexact=dia.lower())

    dias = reportes.values_list('dia_evento', flat=True)
    conteo_dias = Counter(dias)

    dias_ordenados = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    etiquetas = [d.capitalize() for d in dias_ordenados]
    valores = [conteo_dias.get(d, 0) for d in dias_ordenados]

    plt.figure(figsize=(8, 5))
    plt.bar(etiquetas, valores, color='#1976d2')
    plt.xlabel('Día de la semana')
    plt.ylabel('Cantidad de reportes')
    if dia:
        plt.title(f'Reportes filtrados por día: {dia.capitalize()}')
    else:
        plt.title('Cantidad de reportes por día')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_dias_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()
    return grafico_dias_base64

"""
def grafico_promedio_satisfaccion():
    # 🔹 Filtrar solo los registros involucrados
    satisfacciones = Reporte.objects.filter(involucrado_reporte=1).values_list('satisfaccion', flat=True)
    conteo_satisfaccion = Counter(satisfacciones)

    etiquetas_legibles = {
        'muy_deficiente': 'Muy Deficiente',
        'deficiente': 'Deficiente',
        'aceptable': 'Aceptable',
        'bueno': 'Bueno',
        'excelente': 'Excelente'
    }

    orden_categorias = ['muy_deficiente', 'deficiente', 'aceptable', 'bueno', 'excelente']
    etiquetas_satisf = [etiquetas_legibles.get(cat, cat) for cat in orden_categorias if cat in conteo_satisfaccion]
    valores_satisf = [conteo_satisfaccion[cat] for cat in orden_categorias if cat in conteo_satisfaccion]

    # 🔹 Generar gráfico
    plt.figure(figsize=(6, 6))
    plt.pie(valores_satisf, labels=etiquetas_satisf, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return imagen_base64
"""

def grafico_promedio_satisfaccion(filtro=None):
    # 🔹 Filtrar siempre por involucrado_reporte = 1
    if filtro:
        reportes = Reporte.objects.filter(involucrado_reporte=1, satisfaccion=filtro)
    else:
        reportes = Reporte.objects.filter(involucrado_reporte=1)

    categorias = ['muy_deficiente', 'deficiente', 'aceptable', 'bueno', 'excelente']
    conteo = Counter([r.satisfaccion for r in reportes if r.satisfaccion in categorias])

    labels = list(conteo.keys())
    sizes = list(conteo.values())

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return imagen_base64

def grafico_promedio_heridos_muertos(tipo=''):
    # 🔹 Filtrar base con solo registros involucrados
    qs = Reporte.objects.filter(involucrado_reporte=1)

    if tipo == 'heridos':
        promedio = qs.aggregate(prom=Avg('heridos'))['prom'] or 0
        etiquetas = ['Heridos']
        valores = [promedio]
    elif tipo == 'fallecidos':
        promedio = qs.aggregate(prom=Avg('fallecidos'))['prom'] or 0
        etiquetas = ['Muertos']
        valores = [promedio]
    else:
        promedio_heridos = qs.aggregate(prom=Avg('heridos'))['prom'] or 0
        promedio_muertos = qs.aggregate(prom=Avg('fallecidos'))['prom'] or 0
        etiquetas = ['Heridos', 'Muertos']
        valores = [promedio_heridos, promedio_muertos]

    plt.figure(figsize=(6, 6))
    plt.bar(etiquetas, valores, color=['#ff8a80', '#90caf9'])
    plt.ylabel('Promedio')
    plt.title('Promedio de Heridos y Muertos')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return grafico_base64


def grafico_condicion_climatica(clima=''):
    # 🔹 Filtrar base con solo registros involucrados
    if clima:
        queryset = Reporte.objects.filter(involucrado_reporte=1, condicion_clima=clima)
    else:
        queryset = Reporte.objects.filter(involucrado_reporte=1)

    clima_labels = {
        'despejado': 'Despejado',
        'parcialmente nublado': 'Parcialmente nublado',
        'nublado': 'Nublado',
        'lluvia_suave': 'Lluvia suave',
        'tormenta': 'Tormenta o lluvia fuerte',
        'niebla': 'Niebla / neblina',
        'viento_fuerte': 'Viento fuerte'
    }

    clima_counts = {}
    for key in clima_labels.keys():
        count = queryset.filter(condicion_clima=key).count()
        clima_counts[clima_labels[key]] = count

    # 🔹 Generar gráfico
    plt.figure(figsize=(10, 6))
    plt.bar(clima_counts.keys(), clima_counts.values(), color='#26a69a')
    plt.xticks(rotation=45, ha='right')
    plt.title('Cantidad de reportes por condición climática')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    return base64.b64encode(image_png).decode('utf-8')

import io, base64
import matplotlib.pyplot as plt
from collections import Counter
from django.shortcuts import render


def grafico_top_aseguradoras(qs):
    aseguradoras = qs.values_list("nombre_aseguradora", flat=True)
    conteo = Counter(a for a in aseguradoras if a)

    top5 = conteo.most_common(5)
    if not top5:
        return "", []

    etiquetas, valores = zip(*top5)

    plt.figure(figsize=(6, 6))
    plt.bar(etiquetas, valores, color="skyblue")
    plt.title("Top 5 Aseguradoras Más Mencionadas", fontsize=14)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    plt.close()

    return grafico_base64, [a for a, _ in top5]


def analisis_de_datos(request):
    title = "Analisis de reportes"

    servicio_filtro = request.GET.get("servicio", "")
    dia_filtro = request.GET.get("dia", "")
    satisfaccion_filtro = request.GET.get("satisfaccion", "")
    tipo_evento_filtro = request.GET.get("tipo_evento", "ambos")
    aseguradora_filtro = request.GET.get("aseguradora", "")
    clima_filtro = request.GET.get("clima", "")

    dias_semana = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]

    qs = Reporte.objects.filter(involucrado_reporte=1)

    if aseguradora_filtro:
        qs = qs.filter(nombre_aseguradora=aseguradora_filtro)

    # === Gráfico tipo_vehiculo ===
    tipos = qs.values_list("tipo_vehiculo", flat=True)
    conteo_tipos = Counter(tipos)
    etiquetas_tipos = list(conteo_tipos.keys())
    valores_tipos = list(conteo_tipos.values())

    plt.figure(figsize=(6, 6))
    plt.pie(valores_tipos, labels=etiquetas_tipos, autopct="%1.1f%%", startangle=90)
    plt.axis("equal")
    buf1 = io.BytesIO()
    plt.savefig(buf1, format="png")
    buf1.seek(0)
    grafico_base64 = base64.b64encode(buf1.getvalue()).decode("utf-8")
    buf1.close()
    plt.close()

    # === Gráfico hora_evento ===
    horas = qs.values_list("hora_evento", flat=True)
    conteo_horas = Counter(horas)
    etiquetas_horas = list(conteo_horas.keys())
    valores_horas = list(conteo_horas.values())

    plt.figure(figsize=(6, 6))
    plt.pie(valores_horas, labels=etiquetas_horas, autopct="%1.1f%%", startangle=90)
    plt.axis("equal")
    buf2 = io.BytesIO()
    plt.savefig(buf2, format="png")
    buf2.seek(0)
    grafico_hora_base64 = base64.b64encode(buf2.getvalue()).decode("utf-8")
    buf2.close()
    plt.close()

    # === Otros gráficos ===
    grafico_servicios_base64 = servicios_mas_y_menos(servicio_filtro)
    grafico_peor_base64 = servicios_peor_calificados(servicio_filtro)
    grafico_dia_base64 = grafico_dias_con_mas_reportes(dia_filtro)
    grafico_satisf_base64 = grafico_promedio_satisfaccion(satisfaccion_filtro)
    grafico_heridos_muertos_base64 = grafico_promedio_heridos_muertos(tipo_evento_filtro)
    grafico_clima_base64 = grafico_condicion_climatica(clima_filtro)

    # === NUEVO: Top aseguradoras ===
    grafico_top_aseguradoras_base64, lista_aseguradoras = grafico_top_aseguradoras(qs)

    total_reportes = qs.count()

    return render(request, "analisis_de_datos/datos.html", {
        "title": title,
        "grafico_base64": grafico_base64,
        "grafico_hora_base64": grafico_hora_base64,
        "grafico_servicios_base64": grafico_servicios_base64,
        "grafico_peor_base64": grafico_peor_base64,
        "grafico_dia_base64": grafico_dia_base64,
        "grafico_satisf_base64": grafico_satisf_base64,
        "servicio_seleccionado": servicio_filtro,
        "dia_seleccionado": dia_filtro,
        "satisfaccion_seleccionada": satisfaccion_filtro,
        "tipo_evento_seleccionado": tipo_evento_filtro,
        "clima_seleccionado": clima_filtro,
        "grafico_heridos_muertos_base64": grafico_heridos_muertos_base64,
        "grafico_clima_base64": grafico_clima_base64,
        "grafico_top_aseguradoras_base64": grafico_top_aseguradoras_base64,
        "aseguradora_seleccionada": aseguradora_filtro,
        "lista_aseguradoras": lista_aseguradoras,
        "total_reportes": total_reportes,
        "dias_semana": dias_semana,
    })


#Baches


def grafico_top_localidades(localidad_filtro=''):
    queryset = Bache.objects.filter(estado='sin_arreglar')  # Solo sin arreglar

    # Filtro por localidad (si aplica)
    if localidad_filtro:
        queryset = queryset.filter(localidad_id=localidad_filtro)

    # Contar ocurrencias por ID de localidad
    conteo = Counter(queryset.values_list('localidad_id', flat=True))

    # Obtener top 5
    top_5 = conteo.most_common(5)
    ids_localidades = [loc[0] for loc in top_5]
    cantidades = [loc[1] for loc in top_5]

    # Traer los nombres
    nombres_localidades = Localidad.objects.filter(id__in=ids_localidades)
    nombre_dict = {loc.id: loc.nombre for loc in nombres_localidades}
    etiquetas = [nombre_dict.get(id, f"ID {id}") for id in ids_localidades]

    # Graficar
    plt.figure(figsize=(6, 6))
    plt.bar(etiquetas, cantidades, color='mediumslateblue')
    plt.title('Top 5 Localidades con Más Baches Sin Arreglar')
    plt.xlabel('Localidad')
    plt.ylabel('Cantidad de Reportes')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return grafico_base64


def grafico_top_tipos_calle(tipo_calle_filtro=''):
    queryset = Bache.objects.all()

    # Aplicar filtro si se especificó un tipo de calle
    if tipo_calle_filtro:
        queryset = queryset.filter(tipo_calle=tipo_calle_filtro)

    # Contar ocurrencias de tipo_calle
    conteo = Counter(queryset.values_list('tipo_calle', flat=True))

    # Obtener Top 5
    top_5 = conteo.most_common(5)
    etiquetas = [tipo for tipo, _ in top_5]
    cantidades = [cantidad for _, cantidad in top_5]

    # Gráfico
    plt.figure(figsize=(6, 6))
    plt.bar(etiquetas, cantidades, color='darkorange')
    plt.title('Top 5 Tipos de Calle con Más Reportes')
    plt.xlabel('Tipo de Calle')
    plt.ylabel('Cantidad de Reportes')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return grafico_base64


def grafico_estado_baches():
    # Contar los estados
    estados = Bache.objects.values_list('estado', flat=True)
    contador = {"arreglado": 0, "sin_arreglar": 0}
    for estado in estados:
        if estado in contador:
            contador[estado] += 1

    total = sum(contador.values())
    if total == 0:
        return ''  # Evitar división por cero

    labels = ['Arreglado', 'Sin Arreglar']
    sizes = [contador['arreglado'], contador['sin_arreglar']]
    colors = ['#4CAF50', '#F44336']  # Verde y rojo
    explode = (0.05, 0.05)

    # Crear gráfico
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, explode=explode,
           autopct='%1.1f%%', startangle=90, shadow=True)
    ax.axis('equal')
    plt.title('Porcentaje de Baches Arreglados vs Sin Arreglar')

    # Guardar en buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    # Convertir a base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_base64



def grafico_estado_baches_con_proceso():
    # Contar los estados
    estados = Bache.objects.values_list('estado', flat=True)
    contador = {"arreglado": 0, "sin_arreglar": 0, "en_proceso": 0}

    for estado in estados:
        if estado in contador:
            contador[estado] += 1

    total = sum(contador.values())
    if total == 0:
        return ''  # Evitar división por cero

    labels = ['Arreglado', 'Sin Arreglar', 'En Proceso']
    sizes = [contador['arreglado'], contador['sin_arreglar'], contador['en_proceso']]
    colors = ['#4CAF50', '#F44336', '#FFC107']  # Verde, Rojo, Amarillo
    explode = (0.05, 0.05, 0.05)

    # Crear gráfico
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, explode=explode,
           autopct='%1.1f%%', startangle=90, shadow=True)
    ax.axis('equal')
    plt.title('Porcentaje de Baches por Estado (Incluye En Proceso)')

    # Guardar en buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    # Convertir a base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_base64

def grafico_top_localidades_accidentes(localidad_filtro=''):
    queryset = Bache.objects.all()

    # Aplicar filtro si se especifica
    if localidad_filtro:
        queryset = queryset.filter(localidad_id=localidad_filtro)

    # Agrupar y sumar accidentes por localidad
    accidentes_por_localidad = {}
    for bache in queryset:
        if bache.localidad_id:
            accidentes_por_localidad[bache.localidad_id] = accidentes_por_localidad.get(bache.localidad_id, 0) + (bache.accidentes or 0)

    # Obtener top 5 por suma de accidentes
    top_5 = sorted(accidentes_por_localidad.items(), key=lambda x: x[1], reverse=True)[:5]
    ids_localidades = [item[0] for item in top_5]
    sumas_accidentes = [item[1] for item in top_5]

    # Obtener nombres de localidades
    nombres_localidades = Localidad.objects.filter(id__in=ids_localidades)
    nombre_dict = {loc.id: loc.nombre for loc in nombres_localidades}
    etiquetas = [nombre_dict.get(id, f"ID {id}") for id in ids_localidades]

    # Graficar
    plt.figure(figsize=(6, 6))
    plt.bar(etiquetas, sumas_accidentes, color='darkorange')
    plt.title('Top 5 Localidades con Mayor Número de Accidentes')
    plt.xlabel('Localidad')
    plt.ylabel('Total de Accidentes')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return grafico_base64

def grafico_top_localidades_accidentes(localidad_filtro=''):
    queryset = Bache.objects.all()

    # Aplicar filtro si se especifica
    if localidad_filtro:
        queryset = queryset.filter(localidad_id=localidad_filtro)

    # Agrupar y sumar accidentes por localidad
    accidentes_por_localidad = {}
    for bache in queryset:
        if bache.localidad_id:
            accidentes_por_localidad[bache.localidad_id] = accidentes_por_localidad.get(bache.localidad_id, 0) + (bache.accidentes or 0)

    # Obtener top 5 por suma de accidentes
    top_5 = sorted(accidentes_por_localidad.items(), key=lambda x: x[1], reverse=True)[:5]
    ids_localidades = [item[0] for item in top_5]
    sumas_accidentes = [item[1] for item in top_5]

    # Obtener nombres de localidades
    nombres_localidades = Localidad.objects.filter(id__in=ids_localidades)
    nombre_dict = {loc.id: loc.nombre for loc in nombres_localidades}
    etiquetas = [nombre_dict.get(id, f"ID {id}") for id in ids_localidades]

    # Graficar
    plt.figure(figsize=(6, 6))
    plt.bar(etiquetas, sumas_accidentes, color='darkorange')
    plt.title('Top 5 Localidades con Mayor Número de Accidentes')
    plt.xlabel('Localidad')
    plt.ylabel('Total de Accidentes')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return grafico_base64



def grafico_barras_por_mes_estado(filtro_estado=''):
    from collections import defaultdict
    import matplotlib.pyplot as plt
    import io, base64
    #from .models import Bache

    # Establecer el locale a español
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es_CO.UTF-8')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, '')  # Fallback

    datos_mensuales = defaultdict(lambda: {'arreglado': 0, 'en_proceso': 0, 'sin_arreglar': 0})

    queryset = Bache.objects.all()
    if filtro_estado:
        queryset = queryset.filter(estado=filtro_estado)

    for b in queryset:
        if b.created_at:
            mes = b.created_at.month
            estado = b.estado
            if estado in ['arreglado', 'en_proceso', 'sin_arreglar']:
                datos_mensuales[mes][estado] += 1

    meses = [calendar.month_name[i].capitalize() for i in range(1, 13)]
    arreglados = [datos_mensuales[i]['arreglado'] for i in range(1, 13)]
    en_proceso = [datos_mensuales[i]['en_proceso'] for i in range(1, 13)]
    sin_arreglar = [datos_mensuales[i]['sin_arreglar'] for i in range(1, 13)]

    x = range(1, 13)
    plt.figure(figsize=(12, 6))
    plt.bar(x, arreglados, color='green', label='Arreglado')
    plt.bar(x, en_proceso, bottom=arreglados, color='orange', label='En Proceso')
    base_sin_arreglar = [arreglados[i] + en_proceso[i] for i in range(12)]
    plt.bar(x, sin_arreglar, bottom=base_sin_arreglar, color='red', label='Sin Arreglar')

    plt.xticks(x, meses, rotation=45)
    plt.xlabel('Mes')
    plt.ylabel('Cantidad de Baches')
    plt.title('Baches por Estado y Mes')
    plt.legend()

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return grafico_base64

def analisis_baches(request):
    title = 'Analisis de baches'

    localidad_filtro = request.GET.get('localidad', '')
    tipo_calle_filtro = request.GET.get('tipo_calle', '')
    estado_filtro = request.GET.get('estado', '')

    # Establecer el locale a español para que los meses salgan en español en los gráficos
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Linux/Mac
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es_CO.UTF-8')  # Colombia (si disponible)
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Windows
            except locale.Error:
                locale.setlocale(locale.LC_TIME, '')  # Fallback

    grafico_localidades_base64 = grafico_top_localidades(localidad_filtro)
    grafico_tipo_calle_base64 = grafico_top_tipos_calle(tipo_calle_filtro)
    grafico_estado_base64 = grafico_estado_baches()
    grafico_estado_con_proceso_base64 = grafico_estado_baches_con_proceso()
    grafico_localidades_accidentes_base64 = grafico_top_localidades_accidentes(localidad_filtro)
    grafico_barras_estado_mes_base64 = grafico_barras_por_mes_estado(estado_filtro)

    top_ids = [loc[0] for loc in Counter(Bache.objects.values_list('localidad_id', flat=True)).most_common(5)]
    localidades_top = Localidad.objects.filter(id__in=top_ids)
    total_reportes = Bache.objects.count()

    return render(request, 'analisis_de_datos/datos_bache.html', {
        'title': title,
        'total_reportes': total_reportes,
        'grafico_localidades_base64': grafico_localidades_base64,
        'grafico_tipo_calle_base64': grafico_tipo_calle_base64,
        'grafico_estado_base64': grafico_estado_base64,
        'grafico_estado_con_proceso_base64': grafico_estado_con_proceso_base64,
        'grafico_localidades_accidentes_base64': grafico_localidades_accidentes_base64,
        'grafico_barras_estado_mes_base64': grafico_barras_estado_mes_base64,
        'localidades': localidades_top,
        'localidad_seleccionada': localidad_filtro,
        'tipos_calle': Tipo_calle.choices,
        'tipo_calle_seleccionado': tipo_calle_filtro,
        'estado_seleccionado': estado_filtro,
        'opciones_estado': ['sin_arreglar', 'en_proceso', 'arreglado'],
    })



