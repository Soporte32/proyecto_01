from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from estructura.models import Empleado, SolicitudHorasSamic
from .forms import SolicitudHorasSamicForm, AnulacionHorasSamicForm
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q

def sin_permiso(request):
    usuario = request.user
    return not usuario.groups.filter(name__in=['Administradores']).exists()

def sin_permiso_rrhh(request):
    usuario = request.user
    return not usuario.groups.filter(name__in=['Administradores', 'Recursos Humanos']).exists()

def sin_permiso_autorizante(request):
    usuario = request.user
    return not usuario.groups.filter(name__in=['Administradores', 'Autorizantes Licencias']).exists()

@login_required
def rh_inicio(request):
    if sin_permiso_rrhh(request): return HttpResponseRedirect("/")

    usuario = request.user

    # Mostrar el segundo card si pertenece a "Autorizantes Licencias" o "Administradores"
    ja_autorizante = usuario.groups.filter(name__in=['Autorizantes Licencias', 'Administradores']).exists()

    return render(request, 'rh-inicio.html', {'ja_autorizante': ja_autorizante})


@login_required
def solicitar_horas_samic(request):
    if sin_permiso_rrhh(request): return HttpResponseRedirect("/")

    usuario = request.user
    try:
        empleado = Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        return redirect("/")  # o mostrar un error

    success_message = None

    if request.method == 'POST':
        form = SolicitudHorasSamicForm(
            request.POST,
            initial={'usuario': usuario, 'empleado': empleado}
        )
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
            form = SolicitudHorasSamicForm(initial={'usuario': usuario, 'empleado': empleado})
    else:
        form = SolicitudHorasSamicForm(initial={'usuario': usuario, 'empleado': empleado})

    return render(request, 'solicitar-horas-samic.html', {
        'form': form,
        'success_message': success_message
    })


@login_required
def autorizar_horas_samic(request):
    if sin_permiso_autorizante(request): return HttpResponseRedirect("/")

    usuario = request.user
    solicitudes = SolicitudHorasSamic.objects.filter(
        estado="pendiente"
    ).filter(
        Q(empleado__autorizante1=usuario) |
        Q(empleado__autorizante2=usuario) |
        Q(empleado__autorizante3=usuario)
    )

    return render(request, 'autorizar-horas-samic.html', {'solicitudes': solicitudes})


@require_POST
@login_required
def accion_horas_samic(request, solicitud_id):
    if sin_permiso_autorizante(request): return HttpResponseRedirect("/")

    solicitud = get_object_or_404(SolicitudHorasSamic, id=solicitud_id)
    accion = request.POST.get('accion')

    if solicitud.estado == "pendiente":
        if accion == "autorizar":
            solicitud.estado = "autorizada"
        elif accion == "rechazar":
            solicitud.estado = "rechazada"
        solicitud.save()

    return redirect('autorizar-horas-samic')


@login_required
def anular_solicitudes_form(request):
    if sin_permiso_autorizante(request): 
        return HttpResponseRedirect("/")

    solicitudes = []
    if request.method == 'POST':
        form = AnulacionHorasSamicForm(request.POST)
        if form.is_valid():
            empleado = form.cleaned_data['empleado']
            fecha_desde = form.cleaned_data['fecha_desde']
            solicitudes = SolicitudHorasSamic.objects.filter(
                empleado=empleado,
                fecha__gte=fecha_desde,
                estado='autorizada'
            )

            usuario = request.user
            if usuario.groups.filter(name="Autorizantes de Licencias").exists():
                # Filtrar por relación de autorizante
                solicitudes = solicitudes.filter(
                    Q(empleado__autorizante1=usuario) |
                    Q(empleado__autorizante2=usuario) |
                    Q(empleado__autorizante3=usuario)
                )

                # Filtrar por fecha dentro de 4 días desde la fecha de la solicitud
                fecha_limite = timezone.now().date() - timedelta(days=4)
                solicitudes = solicitudes.filter(fecha__gte=fecha_limite)

    else:
        form = AnulacionHorasSamicForm()

    return render(request, 'anular-horas-samic.html', {'form': form, 'solicitudes': solicitudes})


@require_POST
@login_required
def accion_anular_horas_samic(request, solicitud_id):
    if sin_permiso_autorizante(request): return HttpResponseRedirect("/")

    usuario = request.user

    solicitud = get_object_or_404(SolicitudHorasSamic, id=solicitud_id)

    if solicitud.estado == "autorizada":
        solicitud.estado = "anulada"
        solicitud.anulo = usuario
        solicitud.save()
        messages.success(request, f"La solicitud del {solicitud.fecha} fue anulada correctamente.")

    return redirect('anular-horas-samic')

@login_required
def mis_horas_samic(request):
    usuario = request.user
    fecha_desde = request.GET.get('fecha_desde')
    solicitudes = []

    if fecha_desde:
        try:
            fecha_obj = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
            solicitudes = SolicitudHorasSamic.objects.filter(
                empleado__usuario=usuario,
                fecha__gte=fecha_obj
            ).order_by('fecha', 'hora_desde')
        except ValueError:
            pass  # Si la fecha no es válida, no se filtra

    return render(request, 'mis-horas-samic.html', {
        'solicitudes': solicitudes,
        'fecha_desde': fecha_desde,
    })

