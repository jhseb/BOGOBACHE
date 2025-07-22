from django import forms
from .models import Usuario

from django import forms
from .models import Usuario

class usuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')

        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")

        if len(cedula) != 10:
            raise forms.ValidationError("Se necesita 10 digitos")

        return cedula

    

