from django import forms
from estructura.models import Presupuesto

class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ['cliente', 'documento']
        widgets = {
            'cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
        }

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Selecciona un archivo Excel")
