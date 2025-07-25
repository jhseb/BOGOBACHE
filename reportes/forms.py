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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_evento'].input_formats = ['%Y-%m-%d']


        # Estilo para todos los campos visibles
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
