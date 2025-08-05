from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from estructura.models import Empleado
from .forms import SolicitudHorasSamicForm
from datetime import date


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

    if request.method == 'POST':
        form = SolicitudHorasSamicForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = usuario
            solicitud.empleado = empleado
            solicitud.fecha_solicitud = date.today()
            solicitud.estado = 'pendiente'
            solicitud.save()
            
            success_message = "Su solicitud fue generada y está pendiente de autorizar por el responsable de su sector."
            return render(request, 'solicitar-horas-samic.html', {
                'form': SolicitudHorasSamicForm(),  # limpiar formulario
                'success_message': success_message
            })
    else:
        form = SolicitudHorasSamicForm()

    return render(request, 'solicitar-horas-samic.html', {'form': form})
