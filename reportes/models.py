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
    CARRO= 'carro','Carro'
    MOTOCICLETA = 'motocicleta','Motocicleta'
    CAMIONETA = 'camioneta','Camioneta'
    BUSETA = 'buseta', 'Buseta'
    BICICLETA = 'bicicleta', 'Bicileta'
    MOTOTAXI = 'mototaxi', 'mototaxi'
    OTRO = 'otro', 'Otro'

class Danio_Vehicular(models.TextChoices):
    NINGUNO ='ninguno','Ninguno'
    MUY_LEVE='muy_leve','Muy leve (Daños cosmeticos)'
    LEVE = 'leve','Leve (Daños menores)'
    MODERADO ='moderado', 'Moderado (Daños funcionales)'
    GRAVE = 'grave', 'Grave (Daños estructurales mecanicos)'
    PERDIDA_TOTAL = 'perdida_total','Perdida total (Vehiculo irreparable)'

class Danio_Persona(models.TextChoices):
    SIN_LESION = 'sin_lesion', 'Sin lesión'
    LEVE = 'leve', 'Leve (Contusiones menores, sin hospitalización)'
    MODERADA = 'moderada', 'Moderada (Requiere atención médica sin riesgo vital)'
    GRAVE = 'grave', 'Grave (Lesiones críticas o permanentes)'

class CondicionClimatica(models.TextChoices):
    DESPEJADO = 'despejado', 'Despejado'
    PARCIALMENTE_NUBLADO = 'parcialmente nublado', 'Parcialmente nublado'
    NUBLADO = 'nublado', 'Nublado'
    LLUVIA = 'lluvia_suave', 'Lluvia suave'
    TORMENTA = 'tormenta', 'Tormenta o lluvia fuerte'
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

class ManiobraAccidenteBache(models.TextChoices):
    CIRCULABA_NORMAL = 'circulaba_normal', 'Circulaba en línea recta'
    EVITAR_BACHE = 'evitar_bache', 'Intentaba evitar el bache'
    NO_VIO_BACHE = 'no_vio_bache', 'No vio el bache'
    GIRO ='giro', 'Giraba a la derecha/izquierda'
    CAMBIO_CARRIL = 'cambio_carril', 'Cambio de carril'
    FRENADO_BRUSCO = 'frenado_brusco', 'Frenado brusco por el bache'
    PERDIO_CONTROL = 'perdio_control', 'Perdió el control del vehículo'
    PASO_SOBRE_BACHE = 'paso_sobre_bache', 'Pasó directamente sobre el bache'
    RETROCESO = 'retroceso', 'Retrocedía o hacía maniobra en reversa'
    INVASION_SENTIDO = 'invasion_sentido', 'Invadía carril contrario'
    CRUCE_INTERSECCION = 'cruce_interseccion', 'Cruzaba intersección'

class PendienteVia(models.TextChoices):
    PLANA = 'plana', 'Plana'
    MUY_ALTA = 'muy_alta', 'Subida pronunciada'
    ALTA = 'alta', 'Subida leve'
    BAJADA = 'bajada', 'Bajada leve'
    MUY_BAJADA = 'muy_bajada', 'Bajada pronunciada'

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
    PAVIMENTO_RIGIDO = 'pavimento', 'Pavimento rigido'
    PAVIMENTO_DESGASTADO = 'desgastado', 'Pavimento desgastado'
    ADOQUINES = 'adoquines', 'Adoquines'
    TIERRA = 'tierra', 'Tierra'
    GRAVA = 'grava', 'Grava'
    ARENA = 'arena', 'Arena'
    BARRO = 'barro', 'Barro/Lodo'
    PAVIMENTO_RESBALOSO = 'resbaloso', 'Pavimento resbaloso'

class EstadoVia(models.TextChoices):
    BUENA = 'buena', 'Buena'
    REGULAR = 'regular', 'Regular'
    MALA = 'mala', 'Mala'

class ServicioAtencionPolicial(models.TextChoices):
    NO_APLICA = 'no_aplica', 'No_Aplica'
    MUY_DEFICIENTE = 'muy_deficiente', 'Muy deficiente'
    DEFICIENTE = 'deficiente', 'Deficiente'
    REGULAR = 'aceptable', 'Aceptable'
    BUENO = 'bueno', 'Bueno'
    EXCELENTE = 'excelente', 'Excelente'

class ServicioAtencionGrua(models.TextChoices):
    NO_APLICA = 'no_aplica', 'No_Aplica'
    MUY_DEFICIENTE = 'muy_deficiente', 'Muy deficiente'
    DEFICIENTE = 'deficiente', 'Deficiente'
    REGULAR = 'aceptable', 'Aceptable'
    BUENO = 'bueno', 'Bueno'
    EXCELENTE = 'excelente', 'Excelente'

class ServicioAtencionAseguradora(models.TextChoices):
    NO_APLICA = 'no_aplica', 'No_Aplica'
    MUY_DEFICIENTE = 'muy_deficiente', 'Muy deficiente'
    DEFICIENTE = 'deficiente', 'Deficiente'
    REGULAR = 'aceptable', 'Aceptable'
    BUENO = 'bueno', 'Bueno'
    EXCELENTE = 'excelente', 'Excelente'

class ServicioAtencionAbogados(models.TextChoices):
    NO_APLICA = 'no_aplica', 'No_Aplica'
    MUY_DEFICIENTE = 'muy_deficiente', 'Muy deficiente'
    DEFICIENTE = 'deficiente', 'Deficiente'
    REGULAR = 'aceptable', 'Aceptable'
    BUENO = 'bueno', 'Bueno'
    EXCELENTE = 'excelente', 'Excelente'

class ServicioAtencionBomberos(models.TextChoices):
    NO_APLICA = 'no_aplica', 'No_Aplica'
    MUY_DEFICIENTE = 'muy_deficiente', 'Muy deficiente'
    DEFICIENTE = 'deficiente', 'Deficiente'
    REGULAR = 'aceptable', 'Aceptable'
    BUENO = 'bueno', 'Bueno'
    EXCELENTE = 'excelente', 'Excelente'


class SatisfacionExperienciaUsuario(models.TextChoices):
    NO_APLICA = 'no_aplica', 'No_Aplica'
    MUY_DEFICIENTE = 'muy_deficiente', 'Muy deficiente'
    DEFICIENTE = 'deficiente', 'Deficiente'
    REGULAR = 'aceptable', 'Aceptable'
    BUENO = 'bueno', 'Bueno'
    EXCELENTE = 'excelente', 'Excelente'


class ServicioAtencionMedicos(models.TextChoices):
    NO_APLICA = 'no_aplica', 'No_Aplica'
    MUY_DEFICIENTE = 'muy_deficiente', 'Muy deficiente'
    DEFICIENTE = 'deficiente', 'Deficiente'
    REGULAR = 'aceptable', 'Aceptable'
    BUENO = 'bueno', 'Bueno'
    EXCELENTE = 'excelente', 'Excelente'

class Orientacion(models.TextChoices):
    NORTE = 'norte', 'Norte'
    SUR = 'sur', 'Sur'
    ESTE = 'este', 'Este'
    OESTE = 'oeste', 'Oeste'
    NOROESTE = 'noroeste', 'Noroeste'
    NORESTE = 'noreste', 'Noreste'
    SUROESTE = 'suroeste', 'Suroeste'
    SURESTE = 'sureste', 'Sureste'

class AntiguedadVehiculo(models.TextChoices):
    NUEVO = '-1', 'Menos de 1 año'
    RECIENTE = '1-3', '1 a 3 años'
    MODERADO = '4-7', '4 a 7 años'
    ANTIGUO = '8-15', '8 a 15 años'
    MUY_ANTIGUO = '+15', 'Más de 15 años'

class DiaEvento(models.TextChoices):
    LUNES = 'lunes','Lunes'
    MARTES = 'martes','Martes'
    MIERCOLES = 'miercoles','Miercoles'
    JUEVES = 'jueves','Jueves'
    Viernes = 'viernes','Viernes'
    SABADO = 'Sabado'
    DOMINGO = 'Domingo'

class HoraEvento(models.TextChoices):
    MANANA = 'dia', 'Dia (06:00 - 12:00)'
    TARDE = 'tarde', 'Tarde (12:00 - 18:00)'
    NOCHE = 'noche', 'Noche (18:00 - 00:00)'
    MADRUGADA = 'madrugada', 'Madrugada (00:00 - 06:00)'

class DescripcionBache(models.TextChoices):
    BACHE = 'bache', 'bache normal'
    GRIETA = 'grieta', 'Grieta alargada'
    HUNDIMIENTO = 'hundimiento', 'zona hundida'
    PARCHE_DETETERIORADO = 'parche_deteriorado', 'Parche deteriorado'
    MULTIPLES = 'multiples', 'Varios baches en la misma zona'
    CUBIERTO = 'cubierto', 'bache cubierto con material no adecuado'


def generar_id_reporte():
    return 'REP-' + get_random_string(length=8).upper()

class Reporte(models.Model):
    #SI es involucrado debellenar todos los datos, caso contrario no lo hace
    id_report = models.CharField(
        max_length=20,
        default=generar_id_reporte,
        unique=True,
        editable=False,
        primary_key=True
    )
    involucrado_reporte = models.BooleanField(default=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    #Datos reporte
    fecha_evento = models.DateField(blank=True, null=True)
    dia_evento=models.CharField(max_length=100, choices=DiaEvento.choices, default=DiaEvento.LUNES, blank=True, null=True)
    hora_evento=models.CharField(max_length=100, choices=HoraEvento.choices, default=HoraEvento.MADRUGADA, blank=True, null=True)
    usuario = models.ForeignKey("usuario.Usuario", on_delete=models.PROTECT, related_name="reportes")

    #Eventos precedentes al sinisetro
    senializacion_presente = models.BooleanField(default=False, blank=True, null=True)
    estado_problema_vehiculo = models.BooleanField(default=False, blank=True, null=True)
    obstaculo_vial = models.CharField(max_length=100, choices=ObstaculoVial.choices, default=ObstaculoVial.NINGUNO, blank=True, null=True)
    maniobra =  models.CharField(max_length=100, choices=ManiobraAccidenteBache.choices, default=ManiobraAccidenteBache.CIRCULABA_NORMAL, blank=True, null=True)
    velocidad_conduccion = models.CharField(max_length=100, choices=VelocidadConduccion.choices, default=VelocidadConduccion.MODERADA, blank=True, null=True)
    conductor_estado  = models.CharField(max_length=100, choices=EstadoConductor.choices, default=EstadoConductor.NORMAL, blank=True, null=True)
    antiguedadvehiculo=models.CharField(max_length=100, choices=AntiguedadVehiculo.choices, default=AntiguedadVehiculo.NUEVO, blank=True, null=True)
    orientacion=models.CharField(max_length=100, choices=Orientacion.choices, default=Orientacion.SUR, blank=True, null=True)
    semaforo = models.BooleanField(default=False, blank=True, null=True)

        
    #condiciones climaticas del accidente
    iluminacion =  models.CharField(max_length=100, choices=Iluminacion.choices, default=Iluminacion.BUENA, blank=True, null=True)
    condicion_clima =  models.CharField(max_length=100, choices=CondicionClimatica.choices, default=CondicionClimatica.DESPEJADO, blank=True, null=True)
    nivel_trafico = models.CharField(max_length=100, choices= NivelTrafico.choices, default= NivelTrafico.FLUIDO, blank=True, null=True)
    via_estado = models.CharField(max_length=100, choices=  EstadoVia.choices, default=  EstadoVia.BUENA, blank=True, null=True)
    tipo_superficie = models.CharField(max_length=100, choices=TipoSuperficie.choices, default=TipoSuperficie.PAVIMENTO_RIGIDO, blank=True, null=True)
    geometria_via = models.CharField(max_length=100, choices=GeometriaVia.choices, default=GeometriaVia.RECTA, blank=True, null=True)
    pendiente_via = models.CharField(max_length=100, choices= PendienteVia.choices, default= PendienteVia.PLANA, blank=True, null=True)
  

    # Datos del Vehiculo
    licencia = models.BooleanField(default=False)
    tipo_vehiculo = models.CharField(max_length=100, choices=Tipo_vehiculo.choices, default=Tipo_vehiculo.CARRO, blank=True, null=True)
    uso_vehiculo =  models.CharField(max_length=100, choices= UsoVehiculo.choices, default= UsoVehiculo.PARTICULAR, blank=True, null=True)
    compania_aseguradora = models.BooleanField(default=False, blank=True, null=True)


    #Daños internos
    danio_vehicular = models.CharField(max_length=100, choices=Danio_Vehicular.choices, default=Danio_Vehicular.NINGUNO, blank=True, null=True)
    danio_persona = models.CharField(max_length=100, choices=Danio_Persona.choices, default=Danio_Persona.SIN_LESION, blank=True, null=True)
    presencia_defuego = models.BooleanField(default=False, blank=True, null=True)
   

    #Detalles del bache
    
    conocimeinto_tenia = models.BooleanField(default=False, blank=True, null=True)
    descripcion_bache = models.CharField(max_length=100, choices=DescripcionBache.choices, default=DescripcionBache.BACHE, blank=True, null=True)
    bache = models.ForeignKey("bache.Bache", on_delete=models.PROTECT, related_name="reportes")
    encharcado = models.BooleanField(default=False, blank=True, null=True)

    #¿Hubieron Testigos ,heridos u fallecidos?
    testigos = models.PositiveIntegerField(default=0, blank=True, null=True)
    heridos = models.PositiveIntegerField(default=0, blank=True, null=True)
    fallecidos = models.PositiveIntegerField(default=0, blank=True, null=True)
    vehiculos_afectados = models.PositiveIntegerField(default=0, blank=True, null=True) 
    danios_ambiente = models.BooleanField(default=False, blank=True, null=True)
    danios_infraestructura = models.BooleanField(default=False, blank=True, null=True)


    #Servicios presentes
    servicio_policia=models.CharField(max_length=100, choices=ServicioAtencionPolicial.choices, default=ServicioAtencionPolicial.NO_APLICA, blank=True, null=True)
    servicio_grua=models.CharField(max_length=100, choices=  ServicioAtencionGrua.choices, default=  ServicioAtencionGrua.NO_APLICA, blank=True, null=True)
    servicio_aseguradora=models.CharField(max_length=100, choices=ServicioAtencionAseguradora.choices, default=ServicioAtencionAseguradora.NO_APLICA, blank=True, null=True)
    servicio_abogados=models.CharField(max_length=100, choices=ServicioAtencionAbogados.choices, default=ServicioAtencionAbogados.NO_APLICA, blank=True, null=True)
    servicio_bomberos=models.CharField(max_length=100, choices=ServicioAtencionBomberos.choices, default=ServicioAtencionBomberos.NO_APLICA, blank=True, null=True)
    servicio_medicos = models.CharField(max_length=100, choices=ServicioAtencionMedicos.choices, default=ServicioAtencionMedicos.NO_APLICA, blank=True, null=True)
    parte_policial = models.BooleanField(default=False, blank=True, null=True)
    reclamo_formal = models.BooleanField(default=False, blank=True, null=True)
    

    # encuesta de satisfaccion
    satisfaccion = models.CharField(max_length=100, choices=SatisfacionExperienciaUsuario.choices, default=SatisfacionExperienciaUsuario.NO_APLICA, blank=True, null=True)
    
    
   
    
    #Evidencias
    foto1 = models.ImageField(
        upload_to='images/',
        verbose_name='Fotografía del incidente',
        help_text='Suba una imagen clara del accidente (Formatos permitidos: JPG, JPEG, PNG)',
        blank=True, 
        null=True,
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
    