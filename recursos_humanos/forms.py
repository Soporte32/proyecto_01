from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from estructura.models import SolicitudHorasSamic, Horarios_Horas_Samic

class SolicitudHorasSamicForm(forms.ModelForm):
    class Meta:
        model = SolicitudHorasSamic
        fields = ['fecha', 'hora_desde', 'hora_hasta']
        widgets = {
            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Seleccioná la fecha'
                },
                format='%Y-%m-%d'
            ),
            'hora_desde': forms.Select(attrs={'class': 'form-select'}),
            'hora_hasta': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].input_formats = ['%Y-%m-%d']
        self.fields['hora_desde'].queryset = Horarios_Horas_Samic.objects.filter(activo='s')
        self.fields['hora_hasta'].queryset = Horarios_Horas_Samic.objects.filter(activo='s')
        self.fields['hora_desde'].label = "Hora Desde"
        self.fields['hora_hasta'].label = "Hora Hasta"
        self.fields['fecha'].label = "Fecha"

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_desde = cleaned_data.get('hora_desde')
        hora_hasta = cleaned_data.get('hora_hasta')

        # Validación de fecha: no puede ser anterior a hoy
        if fecha and fecha < timezone.localdate():
            self.add_error('fecha', "La fecha no puede ser anterior al día de hoy.")

        # Validación de rango horario
        if hora_desde and hora_hasta:
            desde_time = hora_desde.hora
            hasta_time = hora_hasta.hora

            desde_dt = datetime.combine(datetime.today(), desde_time)
            hasta_dt = datetime.combine(datetime.today(), hasta_time)
            diferencia = hasta_dt - desde_dt

            if diferencia < timedelta(minutes=30):
                self.add_error('hora_hasta', "La duración mínima debe ser de 30 minutos.")
            elif diferencia > timedelta(hours=5):
                self.add_error('hora_hasta', "La duración no puede superar las 5 horas.")
            elif diferencia.total_seconds() <= 0:
                self.add_error('hora_hasta', "La hora hasta debe ser posterior a la hora desde.")

        return cleaned_data
