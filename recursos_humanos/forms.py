from django import forms
from estructura.models import SolicitudVacaciones
from datetime import date

class SolicitudVacacionesForm(forms.ModelForm):
    class Meta:
        model = SolicitudVacaciones
        fields = ['fecha_desde', 'fecha_hasta']

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        hoy = date.today()

        if fecha_desde and fecha_hasta:
            if fecha_hasta <= fecha_desde:
                raise forms.ValidationError("La fecha hasta debe ser posterior a la fecha desde.")

            if fecha_hasta > hoy:
                raise forms.ValidationError("La fecha hasta no puede ser posterior al día de hoy.")
        
        return cleaned_data

