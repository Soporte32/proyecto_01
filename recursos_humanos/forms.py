from django import forms
from estructura.models import SolicitudHorasSamic
from django.utils import timezone
from datetime import timedelta

class SolicitudHorasSamicForm(forms.ModelForm):
    class Meta:
        model = SolicitudHorasSamic
        fields = ['fecha_hora_desde', 'fecha_hora_hasta']
        widgets = {
            'fecha_hora_desde': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'fecha_hora_hasta': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['fecha_hora_desde', 'fecha_hora_hasta']:
            self.fields[field_name].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        fecha_hora_desde = cleaned_data.get('fecha_hora_desde')
        fecha_hora_hasta = cleaned_data.get('fecha_hora_hasta')


        if fecha_hora_desde:
            now = timezone.now()
            if fecha_hora_desde <= now:
                raise forms.ValidationError("La fecha y hora de inicio debe ser posterior al momento actual.")

        if fecha_hora_desde and fecha_hora_hasta:
            if fecha_hora_hasta <= fecha_hora_desde:
                raise forms.ValidationError("La fecha y hora final debe ser posterior a la inicial.")

            diferencia = fecha_hora_hasta - fecha_hora_desde
            if diferencia > timedelta(hours=5):
                raise forms.ValidationError("La diferencia entre las fechas no puede ser mayor a 5 horas.")

        return cleaned_data

