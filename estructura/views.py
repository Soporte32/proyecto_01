from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages


import pandas as pd

from .models import Dia, TipoDia, TipoEmpleado, Empleado
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

def limpiar_valor(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


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

                    # Buscar instancia de TipoEmpleado
                    tipo_empleado_nombre = row.get('Tipo', '').strip()
                    tipo_empleado_obj = None
                    if tipo_empleado_nombre:
                        tipo_empleado_obj = TipoEmpleado.objects.filter(nombre__iexact=tipo_empleado_nombre).first()

                    # Parseo seguro de fechas (dd/mm/yyyy con o sin ceros)
                    fecha_nacimiento = pd.to_datetime(row.get('FechaNacimiento', None), dayfirst=True, errors='coerce')
                    fecha_ingreso = pd.to_datetime(row.get('FechaIngreso', None), dayfirst=True, errors='coerce')                 

                    empleado, created = Empleado.objects.update_or_create(
                        legajo=row['Legajo'],
                        defaults={
                            'nombre': limpiar_valor(row['Nombre']),
                            'apellido': limpiar_valor(row['Apellido']),
                            'telefono': limpiar_valor(row.get('Telefono', '')),
                            'dni': int(dni_sin_puntos),
                            'cuil': limpiar_valor(row['CUIL']),
                            'email': limpiar_valor(row.get('Email', '')),
                            'tipo_empleado': tipo_empleado_obj,
                            'fecha_nacimiento': fecha_nacimiento if pd.notnull(fecha_nacimiento) else None,
                            'matricula': limpiar_valor(row.get('Matricula', '')),
                            'fecha_ingreso': fecha_ingreso if pd.notnull(fecha_ingreso) else None,
                        }
                    )
                    
                messages.success(request, "Archivo procesado correctamente.")

            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")
    else:
        form = ExcelUploadForm()

    return render(request, 'es-importar-empleados.html', {'form': form})