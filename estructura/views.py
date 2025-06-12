from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import *
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

import pandas as pd

from .models import Dia, TipoDia, Empleado
from .forms import AnioForm, DiaForm, TipoDiaUpdateForm, ExcelUploadForm
from datetime import date, timedelta

@login_required
def es_inicio(request):
    usuario = request.user
    if not usuario.groups.filter(name='Administradores').exists():
        return HttpResponseRedirect("/")
    return render(request, "es-inicio.html")

@login_required
def es_calendario(request):
    mensaje = None  # Variable para mostrar mensaje si el año ya existe

    if request.method == "POST":
        form = AnioForm(request.POST)
        if form.is_valid():
            anio = form.cleaned_data["anio"]

            # Validar si ya existen registros para el año solicitado
            if Dia.objects.filter(fecha__year=anio).exists():
                mensaje = f"El año {anio} ya tiene un calendario hecho anteriormente."
                return render(request, "es-mensaje.html", {"titulo": "Calendario Existente","mensaje": mensaje})
        
            # Obtener los tipos de días desde la BD
            tipo_habil = TipoDia.objects.get(id=1)  # ID de "hábil"
            tipo_inhabil = TipoDia.objects.get(id=2)  # ID de "inhábil"        

            # Generar los días del año si no existen
            fecha_actual = date(anio, 1, 1)
            while fecha_actual.year == anio:
                fecha_invertida = fecha_actual.strftime("%Y%m%d")
                tipo_dia = tipo_habil if fecha_actual.weekday() < 5 else tipo_inhabil 
                Dia.objects.create(fecha=fecha_actual, fecha_invertida=fecha_invertida, tipo_dia=tipo_dia)
                fecha_actual += timedelta(days=1)

            mensaje = f"El calendario del año {anio} fue generado."
            return render(request, "es-mensaje.html", {"titulo": "Calendario Generado","mensaje": mensaje})

    else:
        form = AnioForm()

    return render(request, "es-calendario.html", {"form": form})


@login_required
def es_ver_calendario(request):
    form = AnioForm()
    dias = None
    mensaje = None
    
    if request.method == "POST":
        form = AnioForm(request.POST)
        if form.is_valid():
            anio = form.cleaned_data['anio']
            dias = Dia.objects.filter(fecha__year=anio).order_by('fecha_invertida')
            if not dias.exists():
                mensaje = f'No hay registros de días para el año {anio}.'

    return render(request, 'es-ver-calendario.html', {'form': form, 'dias': dias, 'mensaje': mensaje})


@login_required
def es_editar_dia(request):
    dia_form = DiaForm(request.POST or None)
    tipo_dia_form = None
    dia = None
    mensaje = ""

    if request.method == 'POST' and dia_form.is_valid():
        fecha = dia_form.cleaned_data['fecha']
        dia = Dia.objects.filter(fecha=fecha).first()

        if not dia:
            mensaje = "El día no está en el calendario."
        else:
            tipo_dia_form = TipoDiaUpdateForm(instance=dia)

            # 🔍 Depuración: Ver qué datos están llegando en el formulario
            print("Datos recibidos:", request.POST)

            # Si el usuario hace clic en "Actualizar Tipo de Día"
            if 'update_tipo_dia' in request.POST:
                tipo_dia_form = TipoDiaUpdateForm(request.POST, instance=dia)

                if tipo_dia_form.is_valid():
                    print("Formulario válido, guardando cambios...")  # Depuración
                    dia.tipo_dia = tipo_dia_form.cleaned_data['tipo_dia']
                    dia.save()
                    print("¡Cambio guardado con éxito!")
                    mensaje = "El tipo de día se actualizó correctamente."
                    return HttpResponseRedirect('es_editar_dia')

    return render(request, 'es-editar-dia.html', {
        'dia_form': dia_form,
        'tipo_dia_form': tipo_dia_form,
        'dia': dia,
        'mensaje': mensaje
    })

@login_required
def es_importar_empleados(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                df = pd.read_excel(file)

                for _, row in df.iterrows():

                    dni_sin_puntos = str(row['DNI']).replace('.', '')

                    empleado, created = Empleado.objects.update_or_create(
                        legajo=row['Legajo'],
                        defaults={
                            'nombre': row['Nombre'],
                            'apellido': row['Apellido'],
                            'telefono': row.get('Telefono', ''),
                            'dni': int(dni_sin_puntos),
                            'cuil': row['CUIL'],
                            'email': row.get('Email', ''),
                        }
                    )
                    
                messages.success(request, "Archivo procesado correctamente.")

            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")
    else:
        form = ExcelUploadForm()

    return render(request, 'es-importar-empleados.html', {'form': form})