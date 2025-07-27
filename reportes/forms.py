from django import forms
from .models import Reporte

class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = '__all__'
        exclude  =['usuario','bache']
        widgets = {
            # Campo visual: usuario deshabilitado (solo lectura)
            'delete': forms.HiddenInput(),
            'update': forms.HiddenInput(),
            'involucrado': forms.HiddenInput(),
            'fecha_evento': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'senializacion_presente': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'estado_problema_vehiculo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_garantia': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'semaforo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'licencia': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'compania_aseguradora': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'presencia_defuego': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'conocimeinto_tenia': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'encharcado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'danios_ambiente': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'danios_infraestructura': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'parte_policial': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'reclamo_formal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
    
        }
        # Hacer explícito que no son requeridos
        senializacion_presente = forms.BooleanField(required=False)
        estado_problema_vehiculo = forms.BooleanField(required=False)
        semaforo = forms.BooleanField(required=False)
        licencia = forms.BooleanField(required=False)
        compania_aseguradora = forms.BooleanField(required=False)
        presencia_defuego = forms.BooleanField(required=False)
        conocimeinto_tenia = forms.BooleanField(required=False)
        encharcado = forms.BooleanField(required=False)
        danios_ambiente = forms.BooleanField(required=False)
        danios_infraestructura = forms.BooleanField(required=False)
        parte_policial = forms.BooleanField(required=False)
        reclamo_formal = forms.BooleanField(required=False)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_evento'].input_formats = ['%Y-%m-%d']


        # Estilo para todos los campos visibles
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
