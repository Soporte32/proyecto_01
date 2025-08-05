from datetime import datetime, timedelta, time
from estructura.models import Horarios_Horas_Samic  # Ajustá el import según tu estructura

def crear_horarios():
    hora_actual = datetime.combine(datetime.today(), time(0, 0))
    fin_dia = datetime.combine(datetime.today(), time(23, 45))
    delta = timedelta(minutes=15)

    while hora_actual <= fin_dia:
        hora_sola = hora_actual.time()

        if time(8, 0) <= hora_sola <= time(17, 0):
            estado = 's'
        else:
            estado = 'n'

        Horarios_Horas_Samic.objects.get_or_create(
            hora=hora_sola,
            defaults={'activo': estado}
        )

        hora_actual += delta

    print("✅ Horarios creados con campo 'activo' correctamente asignado.")

