from django import forms
from .models import Usuario

from django import forms
from .models import Usuario
from .models import Documento,Documento_admin
class usuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')

        # Validar que contenga solo números
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")

        # Validar que la longitud esté entre 5 y 10 dígitos
        if len(cedula) < 5 or len(cedula) > 10:
            raise forms.ValidationError("La cédula debe tener entre 5 y 10 dígitos.")

        return cedula



class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'archivo']

class DocumentoFormAdmin(forms.ModelForm):
    class Meta:
        model = Documento_admin
        fields = ['titulo', 'archivo']