from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from estructura.models import Empleado
from .forms import SolicitudHorasSamicForm
from datetime import date, datetime

@login_required
def rh_inicio(request):
    usuario = request.user
    if not usuario.groups.filter(name='Recursos Humanos').exists():
        return HttpResponseRedirect("/")
    return render(request, 'rh-inicio.html')

@login_required
def solicitar_horas_samic(request):
    usuario = request.user
    try:
        empleado = Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        return redirect("/")  # o mostrar un error

    success_message = None

    if request.method == 'POST':
        form = SolicitudHorasSamicForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = usuario
            solicitud.empleado = empleado
            solicitud.fecha_solicitud = date.today()
            solicitud.estado = 'pendiente'

            # 👉 Cálculo de minutos solicitados
            hora_desde = solicitud.hora_desde.hora
            hora_hasta = solicitud.hora_hasta.hora
            dt_desde = datetime.combine(datetime.today(), hora_desde)
            dt_hasta = datetime.combine(datetime.today(), hora_hasta)
            diferencia = dt_hasta - dt_desde
            solicitud.minutos_solicitados = int(diferencia.total_seconds() / 60)

            solicitud.save()

            success_message = (
                "Su solicitud fue generada y está pendiente de autorizar "
                "por el responsable de su sector."
            )
            form = SolicitudHorasSamicForm()  # reiniciar formulario limpio
    else:
        form = SolicitudHorasSamicForm()

    return render(request, 'solicitar-horas-samic.html', {
        'form': form,
        'success_message': success_message
    })
