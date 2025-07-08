from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

import pandas as pd

from .models import Dia, TipoDia, TipoEmpleado, Empleado
from .forms import AnioForm, DiaForm, TipoDiaUpdateForm, ExcelUploadForm
from datetime import date, timedelta
from django.contrib.auth.models import User

from django.db import transaction


def sin_permiso(request):
    usuario = request.user
    return not usuario.groups.filter(name='Administradores').exists()


@login_required
def es_inicio(request):
    if sin_permiso(request): return HttpResponseRedirect("/")
    
    return render(request, "es-inicio.html")

@login_required
def es_calendario(request):
    if sin_permiso(request): return HttpResponseRedirect("/")
        
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
    if sin_permiso(request): return HttpResponseRedirect("/")
        
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
    if sin_permiso(request): return HttpResponseRedirect("/")
        
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

import psutil, os

@login_required
def es_importar_empleados(request):
    if sin_permiso(request): return HttpResponseRedirect("/")  
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                df = pd.read_excel(file)

                for _, row in df.iterrows():
                    try:
                        with transaction.atomic():
                            nombre = limpiar_valor(row['Nombre']).strip()
                            apellido = limpiar_valor(row['Apellido']).strip()
                            legajo_str = str(row['Legajo'])
                            dni_str = str(row['DNI']).replace('.', '')
                            cuil = limpiar_valor(row['CUIL'])

                            # Verificar si ya existe un empleado con el mismo DNI
                            if Empleado.objects.filter(dni=int(dni_str)).exclude(legajo=row['Legajo']).exists():
                                print(f"Ya existe un empleado con DNI {dni_str}. Omitido legajo {row['Legajo']}.")
                                continue

                            # Username: primera letra del nombre + primer palabra del apellido
                            primer_letra_nombre = nombre[0].lower()
                            primer_palabra_apellido = apellido.split()[0].lower()
                            username = f"{primer_letra_nombre}{primer_palabra_apellido}"

                            usuario_obj = User.objects.filter(username=username).first()

                            # Crear usuario si no existe
                            if not usuario_obj:
                                dni_digitos = dni_str.zfill(8)  # asegurar longitud
                                password = (
                                    f"{nombre[0].upper()}"
                                    f"{primer_palabra_apellido[0].lower()}"
                                    f"{dni_digitos[0]}"
                                    f"{legajo_str[-1]}"
                                    f"{dni_digitos[-2:]}"
                                )
                                usuario_obj = User.objects.create_user(
                                    username=username,
                                    password=password,
                                    first_name=nombre,
                                    last_name=apellido,
                                    email=limpiar_valor(row.get('Email', '')),
                                )
                            else:
                                usuario_obj = None  # Usuario existe: no lo vinculamos

                            tipo_empleado_nombre = row.get('Tipo', '').strip()
                            tipo_empleado_obj = TipoEmpleado.objects.filter(nombre__iexact=tipo_empleado_nombre).first() if tipo_empleado_nombre else None

                            fecha_nacimiento = pd.to_datetime(row.get('FechaNacimiento', None), dayfirst=True, errors='coerce')
                            fecha_ingreso = pd.to_datetime(row.get('FechaIngreso', None), dayfirst=True, errors='coerce')

                            Empleado.objects.update_or_create(
                                legajo=row['Legajo'],
                                defaults={
                                    'nombre': nombre,
                                    'apellido': apellido,
                                    'telefono': limpiar_valor(row.get('Telefono', '')),
                                    'dni': int(dni_str),
                                    'cuil': cuil,
                                    'email': limpiar_valor(row.get('Email', '')),
                                    'tipo_empleado': tipo_empleado_obj,
                                    'fecha_nacimiento': fecha_nacimiento if pd.notnull(fecha_nacimiento) else None,
                                    'matricula': limpiar_valor(row.get('Matricula', '')),
                                    'fecha_ingreso': fecha_ingreso if pd.notnull(fecha_ingreso) else None,
                                    'usuario': usuario_obj,
                                }
                            )
                    except Exception as e:
                        print(f"Error al importar legajo {row['Legajo']}: {e}")

                messages.success(request, "Archivo procesado correctamente.")
            except Exception as e:
                messages.error(request, f"Error general al procesar el archivo: {e}")
        else:
            messages.error(request, "Formulario inválido.")
    else:
        form = ExcelUploadForm()

    return render(request, 'es-importar-empleados.html', {'form': form})