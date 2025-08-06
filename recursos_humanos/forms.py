from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from estructura.models import SolicitudHorasSamic, Horarios_Horas_Samic, Empleado

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

            if diferencia.total_seconds() <= 0:
                self.add_error('hora_hasta', "La hora hasta debe ser posterior a la hora desde.")

        # Validaciones adicionales
        usuario = self.initial.get('usuario')
        empleado = self.initial.get('empleado')

        if usuario and empleado and fecha:
            mes = fecha.month
            año = fecha.year

            # 1️⃣ Validar que no haya solicitud pendiente del mismo usuario
            existe_pendiente = SolicitudHorasSamic.objects.filter(
                usuario=usuario,
                empleado=empleado,
                estado='pendiente'
            ).exists()
            if existe_pendiente:
                raise forms.ValidationError("Ya existe una solicitud pendiente para este usuario.")

            # 2️⃣ Validar que no se superen los 300 minutos en el mes (excluyendo anuladas)
            total_minutos = SolicitudHorasSamic.objects.filter(
                usuario=usuario,
                empleado=empleado,
                fecha__year=año,
                fecha__month=mes
            ).exclude(estado='anulada').aggregate(total=Sum('minutos_solicitados'))['total'] or 0

            if hora_desde and hora_hasta:
                minutos_actual = int((datetime.combine(datetime.today(), hora_hasta.hora) - datetime.combine(datetime.today(), hora_desde.hora)).total_seconds() / 60)
                if total_minutos + minutos_actual > 300:
                    raise forms.ValidationError("No puede solicitar más de 5 horas en el mismo mes.")

            # 3️⃣ Validar que no haya más de 4 solicitudes en el mes (excluyendo anuladas)
            cantidad_solicitudes = SolicitudHorasSamic.objects.filter(
                usuario=usuario,
                empleado=empleado,
                fecha__year=año,
                fecha__month=mes
            ).exclude(estado='anulada').count()

            if cantidad_solicitudes >= 4:
                raise forms.ValidationError("No puede realizar más de 4 solicitudes en el mismo mes.")

        return cleaned_data


class AnulacionHorasSamicForm(forms.Form):
    empleado = forms.ModelChoiceField(queryset=Empleado.objects.all(), required=True, label="Empleado")
    fecha_desde = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label="Fecha desde")

