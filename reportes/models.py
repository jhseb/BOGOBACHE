from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from bache.models import Bache
from usuario.models import Usuario

class Tipo_vehiculo(models.TextChoices):
    CARRO_PARTICULAR= 'carro_particular','Carro particular'
    MOTOCICLETA = 'motocicleta','Motocicleta'
    CAMIONETA = 'camioneta','Camioneta'
    BUSETA = 'buseta', 'Buseta'
    BICICLETA = 'bicicleta', 'Bicileta'
    MOTOTAXI = 'mototaxi', 'mototaxi'

class Danio_Vehicular(models.IntegerChoices):

    MUY_LEVE=1,'Muy leve (Daños cosmeticos)'
    LEVE = 2,'Leve (Daños menores)'
    MODERADO =3, 'Moderado (Daños funcionales)'
    GRAVE = 4, 'Grave (Daños estructurales mecanicos)'
    PERDIDA_TOTAL = 5,'Perdida total (Vehiculo irreparable)'

class Danio_Persona(models.IntegerChoices):
    SIN_LESION = 1, 'Sin lesión'
    LEVE = 2, 'Leve (Contusiones menores, sin hospitalización)'
    MODERADA = 3, 'Moderada (Requiere atención médica sin riesgo vital)'
    GRAVE = 4, 'Grave (Lesiones críticas o permanentes)'
    FALLECIMIENTO = 5, 'Fallecimiento (Muerte en el sitio o posterior)'

class CondicionClimatica(models.TextChoices):
    DESPEJADO = 'despejado', 'Despejado'
    PARCIALMENTE_NUBLADO = 'parcialmente nublado', 'Parcialmente nublado'
    NUBLADO = 'nublado', 'Nublado'
    LLUVIA = 'lluvioso', 'Lluvioso'
    TORMENTA = 'tormenta', 'Tormenta'
    NIEBLA = 'niebla', 'Niebla / neblina'
    VIENTO_FUERTE = 'viento_fuerte', 'Viento fuerte'

class VelocidadConduccion(models.TextChoices):
    MUY_BAJA = 'muy_baja', 'Muy baja (0-20 km/h)'
    BAJA = 'baja', 'Baja (21-40 km/h)'
    MODERADA = 'moderada', 'Moderada (41-60 km/h)'
    ALTA = 'alta', 'Alta (61-80 km/h)'
    MUY_ALTA = 'muy_alta', 'Muy alta / Excesiva (81+ km/h)'

class EstadoConductor(models.TextChoices):
    NORMAL = 'normal', 'En condiciones normales'
    CANSADO = 'cansado', 'Cansado o somnoliento'
    DISTRAIDO = 'distraido', 'Distraído'
    ALCOHOL = 'alcoholizado', 'Bajo efecto de alcohol'
    ANSIOSO = 'ansioso', 'Ansioso'
    DEPRESIVO = 'depresivo','Depresivo'
    ENOJADO = 'enojado', 'Enojado'
    ESTRESADO = 'estresado', 'Estresado'
    DROGAS = 'drogado', 'Bajo efecto de drogas'
    DISCAPACIDAD = 'discapacidad visual', 'Con discapacidad visible'

class DireccionFlujo(models.TextChoices):
    UNIDIRECCIONAL = 'Unidireccional', 'Unidireccional'
    BIDIRECCIONAL = 'Bidireccional', 'Bidireccional'
    REVERSIBLE = 'Reversible', 'Reversible'
    ROTACIONAL = 'Rotacional', 'Rotacional (glorieta)'
    RESTRINGIDO = 'Restringido', 'Restringido o cerrado'

class PendienteVia(models.TextChoices):
    PLANA = 'plana', 'Plana'
    SUBIDA = 'subida', 'Subida'
    BAJADA = 'bajada', 'Bajada'
    VARIABLE = 'variable', 'Variable'
    DESCONOCIDA = 'desconocida', 'Desconocida / No aplica'

class GeometriaVia(models.TextChoices):
    RECTA = 'recta', 'Recta'
    CURVA_ABIERTA = 'curva_abierta', 'Curva abierta'
    CURVA_CERRADA = 'curva_cerrada', 'Curva cerrada'
    MULTIPLES_CURVAS = 'multiples_curvas', 'Múltiples curvas / Zigzag'
    DESCONOCIDA = 'desconoida', 'Desconocida'

class UsoVehiculo(models.TextChoices):
    PARTICULAR = 'particular', 'Particular'
    PUBLICO = 'transporte_publico', 'Transporte público'
    TAXI = 'taxi', 'Taxi'
    CARGA = 'logistica', 'Carga / Logística'
    ESCOLAR = 'escolar', 'Escolar'
    EMERGENCIA = 'emergencia', 'Emergencia'
    OFICIAL = 'institucional', 'Oficial / Institucional'
    DOMICILIO = 'domiciliario', 'vehiculo de reparto / Mensajería'
    TURISMO = 'turismo_o_especial', 'Turismo / Especial'
    PRIVADO = 'plataforma_digital','Plataforma digital'
    APRENDIZAJE ='aprendizaje','Aprendizaje / Escuela'

class Iluminacion(models.TextChoices):
    BUENA = 'buena', 'Buena'
    MODERADA = 'moderada', 'Moderada'
    POBRE = 'pobre', 'Pobre'

class ObstaculoVial(models.TextChoices):
    NINGUNO = 'Ninguno', 'Ninguno'
    VEHICULO_DETENIDO = 'vehiculo_detenido', 'Vehículo detenido'
    MATERIAL = 'material_en_via', 'Material en la vía'
    ANIMAL = 'animal', 'Animal'
    PERSONA = 'persona', 'Persona'
    OBRA = 'obra_vial', 'Obra vial'
    VEGETACION = 'vegetacion', 'Árbol o vegetación'

class NivelTrafico(models.TextChoices):
    FLUIDO = 'fluido', 'Fluido'
    MODERADO = 'moderado', 'Moderado'
    CONGESTIONADO = 'congestionado', 'Congestionado'
    DETENIDO = 'detenido', 'Detenido'

class TipoSuperficie(models.TextChoices):
    PAVIMENTO_RIGIDO = 'pavimento_rigido', 'Pavimento rígido (concreto)'
    PAVIMENTO_FLEXIBLE = 'pavimento_flexible', 'Pavimento flexible (asfalto)'
    ADOQUINES = 'adoquines', 'Adoquines'
    TIERRA = 'tierra', 'Tierra'
    GRAVA = 'grava', 'Grava'
    ARENA = 'arena', 'Arena'
    BARRO = 'barro', 'Barro/Lodo'

class EstadoVia(models.TextChoices):
    BUENA = 'buena', 'Buena'
    REGULAR = 'regular', 'Regular'
    MALA = 'mala', 'Mala'
    EN_MANTENIMIENTO = 'mantenimiento', 'En mantenimiento'
    OBSTRUIDA = 'obstruida', 'Obstruida'
    RESBALADIZA ='resbaloza','resbaloza'

class ServicioAtencionPolicial(models.IntegerChoices):
    NO_APLICA = 0, 'No_Aplica'
    MUY_DEFICIENTE = 1, 'Muy deficiente'
    DEFICIENTE = 2, 'Deficiente'
    REGULAR = 3, 'Aceptable'
    BUENO = 4, 'Bueno'
    EXCELENTE = 5, 'Excelente'

class ServicioAtencionGrua(models.IntegerChoices):
    NO_APLICA = 0, 'No_Aplica'
    MUY_DEFICIENTE = 1, 'Muy deficiente'
    DEFICIENTE = 2, 'Deficiente'
    REGULAR = 3, 'Aceptable'
    BUENO = 4, 'Bueno'
    EXCELENTE = 5, 'Excelente'

class ServicioAtencionAseguradora(models.IntegerChoices):
    NO_APLICA = 0, 'No_Aplica'
    MUY_DEFICIENTE = 1, 'Muy deficiente'
    DEFICIENTE = 2, 'Deficiente'
    REGULAR = 3, 'Aceptable'
    BUENO = 4, 'Bueno'
    EXCELENTE = 5, 'Excelente'

class ServicioAtencionBomberos(models.IntegerChoices):
    NO_APLICA = 0, 'No_Aplica'
    MUY_DEFICIENTE = 1, 'Muy deficiente'
    DEFICIENTE = 2, 'Deficiente'
    REGULAR = 3, 'Aceptable'
    BUENO = 4, 'Bueno'
    EXCELENTE = 5, 'Excelente'

class ServicioAtencionMedicos(models.IntegerChoices):
    NO_APLICA = 0, 'No_Aplica'
    MUY_DEFICIENTE = 1, 'Muy deficiente'
    DEFICIENTE = 2, 'Deficiente'
    REGULAR = 3, 'Aceptable'
    BUENO = 4, 'Bueno'
    EXCELENTE = 5, 'Excelente'

class Orientacion(models.TextChoices):
    NORTE = 'norte', 'Norte'
    SUR = 'sur', 'Sur'
    ESTE = 'este', 'Este'
    OESTE = 'oeste', 'Oeste'
    NOROESTE = 'noroeste', 'Noroeste'
    NORESTE = 'noreste', 'Noreste'
    SUROESTE = 'suroeste', 'Suroeste'
    SURESTE = 'sureste', 'Sureste'

class AntiguedadVehiculo(models.IntegerChoices):
    NUEVO = 1, 'Menos de 1 año'
    RECIENTE = 2, '1 a 3 años'
    MODERADO = 3, '4 a 7 años'
    ANTIGUO = 4, '8 a 15 años'
    MUY_ANTIGUO = 5, 'Más de 15 años'

def generar_id_reporte():
    return 'REP-' + get_random_string(length=8).upper()

class Reporte(models.Model):
    id_report = models.CharField(
        max_length=20,
        default=generar_id_reporte,
        unique=True,
        editable=False,
        primary_key=True
    )

    usuario = models.ForeignKey("usuario.Usuario", on_delete=models.PROTECT, related_name="reportes")
    bache = models.ForeignKey("bache.Bache", on_delete=models.PROTECT, related_name="reportes")

    involucrado_reporte = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    senializacion_presente = models.BooleanField(default=False)
    licencia = models.CharField(max_length=100, null=True, blank=True)
    telefono_emergencia = models.PositiveIntegerField(default=0)
    matricula_vehiculo = models.CharField(max_length=100, null=True, blank=True)
    compania_aseguradora = models.BooleanField(default=False)
    id_seguro_aseguradora = models.CharField(max_length=100, null=True, blank=True)
    testigos = models.PositiveIntegerField(default=0)
    heridos = models.PositiveIntegerField(default=0)
    datos_testigos = models.CharField(max_length=200, null=True, blank=True)
    datos_heridos = models.CharField(max_length=200, null=True, blank=True)

    tiempo_respuesta_policia = models.DurationField(null=True, blank=True)
    tiempo_respuesta_grua = models.DurationField(null=True, blank=True)
    tiempo_respuesta_aseguradora = models.DurationField(null=True, blank=True)
    tiempo_respuesta_bomberos = models.DurationField(null=True, blank=True)
    tiempo_respuesta_medicos = models.DurationField(null=True, blank=True)

    parte_policial = models.BooleanField(default=False)
    id_parte_policial = models.CharField(max_length=100, null=True, blank=True)

    danio_fisico_personal = models.BooleanField(default=False)
    reclamo_formal = models.BooleanField(default=False)
    abogado_presente = models.BooleanField(default=False)
    vehiculos_afectados = models.PositiveIntegerField(default=0)
    datos_vehiculos = models.CharField(max_length=100, null=True, blank=True)
    danios_ambiente = models.BooleanField(default=False)
    conocimeinto_tenia = models.BooleanField(default=False)
    estado_problema_vehiculo = models.BooleanField(default=False)

    foto1 = models.ImageField(
        upload_to='images/',
        verbose_name='Fotografía del incidente',
        help_text='Suba una imagen clara del accidente (Formatos permitidos: JPG, JPEG, PNG)',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    foto2 = models.ImageField(
        upload_to='images/',
        verbose_name='Fotografía del incidente 2',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    foto3 = models.ImageField(
        upload_to='images/',
        verbose_name='Fotografía del incidente 3',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return self.id_report