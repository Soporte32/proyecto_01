from django import forms
from .models import Dia, TipoDia

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Selecciona un archivo Excel")

class AnioForm(forms.Form):
    anio = forms.IntegerField(label="Ingrese un año", min_value=2016, max_value=2040)

class DiaForm(forms.ModelForm):
    class Meta:
        model = Dia
        fields = ['fecha']

class TipoDiaUpdateForm(forms.ModelForm):
    class Meta:
        model = Dia
        fields = ['tipo_dia']
        widgets = {
            'tipo_dia': forms.Select(attrs={'class': 'form-control'}),
        }

