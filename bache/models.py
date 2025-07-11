from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
# Create your models here.
'''
BACHE

id_bache                          Int - Primary Key
latitud                           Float -
longitud                          Float-
localidad                         Varchar-
direccion                         Varchar-
accidentes                        Int-
diametro                          Float-
estado                            Varchar-
peligrosidad                      Varchar-
foto                              Picture-
'''
class Localidad(models.TextChoices):
    USAQUEN = "Usaquen"
    CHAPINERO = "Chapinero"
    SANTA_FE = "Santa Fe"
    SAN_CRISTOBAL = "San Cristobal"
    USME = "Usme"
    TUNJUELITO = "Tunjuelito"
    BOSA = "Bosa"
    KENNEDY = "Kennedy"
    FONTIBON = "Fontibon"
    ENGATIVA = "Engativa"
    SUBA = "Suba"
    BARRIOS_UNIDOS = "Barrios Unidos"
    TEUSAQUILLO = "Teusaquillo"
    LOS_MARTIRES = "Los Martires"
    ANTONIO_NARINO = "Antonio Narino"
    PUENTE_ARANDA = "Puente Aranda"
    LA_CANDELARIA = "La Candelaria"
    RAFAEL_URIBE_URIBE = "Rafael Uribe Uribe"
    CIUDAD_BOLIVAR = "Ciudad Bolívar"
    SUMAPAZ = "Sumapaz"

class Peligrosidad(models.TextChoices):
    ALTO = "Alto"
    MEDIO = "Medio"
    BAJO = "Bajo"

class Estado(models.TextChoices):
    SIN_ARREGLAR = "sin_arreglar"
    EN_PROCESO = "en_proceso"
    ARREGLADO = "arreglado"

class Bache(models.Model):
    localidad = models.CharField(max_length=100, choices=Localidad.choices, default=Localidad.USAQUEN)

    estado = models.CharField(max_length=100, choices=Estado.choices, default=Estado.SIN_ARREGLAR)

    peligrosidad = models.CharField(max_length=100, choices=Peligrosidad.choices, default=Peligrosidad.BAJO)

    direccion = models.CharField(max_length=100)

    latitud = models.DecimalField(max_digits=25, decimal_places=20, verbose_name='latitud', null=False, blank=False)

    longitud = models.DecimalField(max_digits=25, decimal_places=20, verbose_name='longitud', null=False, blank=False)

    diametro = models.DecimalField(max_digits=15, decimal_places=10, verbose_name='diametro', null=False, blank=False)

    accidentes = models.PositiveIntegerField(default=0, null=False, blank=False)

  
    foto = models.ImageField(
        upload_to='images/',
        verbose_name='Fotografía del incidente',
        help_text='Suba una imagen clara del accidente (Formatos permitidos: JPG, JPEG, PNG)',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        ]
    )
    id_bache = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
        verbose_name='ID del Bache',
        help_text='Identificador único con formato BHC seguido de 5 letras mayúsculas',
        primary_key=True
    )

    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    deleted_at= models.DateTimeField(null=True,auto_now=True)

    def generar_id_bache(self):
        """Genera un ID BHCXXXXX único con 5 letras aleatorias"""
        while True:
            # Genera el ID con letras permitidas (excluye I y O)
            nuevo_id = 'BHC' + get_random_string(
                5,
                allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ'
            )
            # Verifica que no exista en la base de datos
            if not Bache.objects.filter(id_bache=nuevo_id).exists():
                return nuevo_id

def save(self, *args, **kwargs):
    if not self.id_bache:
        self.id_bache = self.generar_id_bache()
    super().save(*args, **kwargs)

def clean(self):
    """Valida el formato correcto del ID"""
    if (len(self.id_bache) != 8 or
        not self.id_bache.startswith('BHC') or
        not self.id_bache[3:].isalpha() or
        any(c in self.id_bache[3:] for c in 'IO')):
        raise ValidationError(
            "El ID debe tener formato BHC seguido de 5 letras mayúsculas (excluyendo I y O). Ejemplo: BHCQAZWS"
        )

class Meta:
    verbose_name = 'Bache'
    verbose_name_plural = 'Baches'
    ordering = ['id_bache']