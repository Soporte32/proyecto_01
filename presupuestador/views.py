import os
import pandas as pd
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from estructura.models import Presupuesto, Prestacion, PresupuestoItem, PresupuestoPrestacion
from datetime import date
from django.db.models import F, Sum
from django.contrib import messages
from .forms import PresupuestoForm, ExcelUploadForm
from decimal import Decimal, InvalidOperation
import numpy as np  # Importa numpy para manejar NaN
from openpyxl.styles import NamedStyle
import openpyxl
from django.http import HttpResponseRedirect

def sin_permiso(request):
    usuario = request.user
    return not usuario.groups.filter(name__in=['Administradores', 'Presupuestos']).exists()

@login_required
def presupuesto_nuevo(request):
    if sin_permiso(request): return HttpResponseRedirect("/")

    if request.method == 'POST':
        # Obtiene los datos del formulario
        cliente = request.POST.get('cliente')
        documento = request.POST.get('documento')

        if cliente and documento:
            # Crea un nuevo presupuesto
            presupuesto = Presupuesto(
                cliente=cliente,
                documento=documento,
                fecha=date.today(),
                creado_por=request.user
            )
            presupuesto.save()
            # Redirige a la vista de lista de presupuestos
            return redirect('detalle_presupuestador')

    # Renderiza la plantilla con datos adicionales (si es necesario)
    return render(request, 'presupuesto_nuevo.html', {
        'fecha_hoy': date.today().strftime('%Y-%m-%d')  # Enviar fecha actual como string
    })

@login_required
def detalle_presupuestador(request):
    if sin_permiso(request): return HttpResponseRedirect("/")
        
    presupuestos = Presupuesto.objects.all()  # Obtén todos los presupuestos
    return render(request, 'detalle_presupuestador.html', {
        'presupuestos': presupuestos,
        'mostrar_volver': True  # Agrega una bandera para mostrar el botón
    })


@login_required
def agregar_item(request, presupuesto_id):
    if sin_permiso(request): return HttpResponseRedirect("/")

    presupuesto = get_object_or_404(Presupuesto, pk=presupuesto_id)

    if request.method == 'POST':
        detalle = request.POST.get('detalle')
        cantidad = request.POST.get('cantidad')
        precio_form = request.POST.get('precio') or '0.00'
        prestacion_id = request.POST.get('prestacion')

        if cantidad and prestacion_id:
            prestacion = get_object_or_404(Prestacion, pk=prestacion_id)

            # Determinar el precio correcto
            if prestacion.codigo == '999.99.99':
                precio = Decimal(precio_form)
            else:
                precio = Decimal(prestacion.total or 0.00)  # Precio desde Prestacion            

            # Crear un nuevo Item
            item = PresupuestoItem.objects.create(
                presupuesto=presupuesto,
                cantidad=cantidad,
                detalle=detalle,
                precio=precio,
                creado_por=request.user
            )

            # Asociar el item con DetallePrestacion
            PresupuestoPrestacion.objects.create(
                presupuesto=presupuesto,
                prestacion=prestacion,
                item=item
            )

        # Aquí usamos presupuesto.numero en lugar de presupuesto.id
        return redirect('detalle_presupuesto', presupuesto_id=presupuesto.numero)

    servicios = Prestacion.objects.values('servicio').distinct().order_by('servicio')

    return render(request, 'agregar_item.html', {
        'presupuesto': presupuesto,
        'servicios': servicios,
    })

@login_required
def eliminar_item(request, presupuesto_id):
    if sin_permiso(request): return HttpResponseRedirect("/")
        
    if request.method == "POST":
        item_id = request.POST.get("item_id")  # Obtén el ID del ítem desde el formulario
        detalle = get_object_or_404(PresupuestoPrestacion, pk=item_id, presupuesto_id=presupuesto_id)

        # Elimina el ítem
        detalle.delete()

        # Muestra un mensaje de éxito
        messages.success(request, "El ítem se eliminó correctamente.")

    # Redirige al detalle del presupuesto
    return redirect("detalle_presupuesto", presupuesto_id=presupuesto_id)

@login_required
def detalle_presupuesto(request, presupuesto_id):
    if sin_permiso(request): return HttpResponseRedirect("/")

    # Obtiene el presupuesto o lanza un error 404 si no existe
    presupuesto = get_object_or_404(Presupuesto, pk=presupuesto_id)
    
    # Obtiene los detalles del presupuesto, optimizando con select_related
    detalles = PresupuestoPrestacion.objects.filter(presupuesto=presupuesto).select_related('prestacion', 'item')

    # Añadir el total de cada línea al queryset
    for detalle in detalles:
        detalle.total_linea = detalle.item.cantidad * detalle.item.precio
        
    # Calcula el total general usando anotaciones
    total_general = detalles.aggregate(
        total=Sum(F('item__cantidad') * F('item__precio'))
    )['total'] or 0

    # Bandera para saber si estamos en modo edición (se puede activar desde la URL)
    modo_edicion = request.GET.get('modo_edicion') == 'true'

    # Renderiza la plantilla con los datos necesarios
    return render(request, 'detalle_presupuesto.html', {
        'presupuesto': presupuesto,
        'detalles': detalles,
        'total_general': total_general,
        'modo_edicion': modo_edicion  # Determina si se muestran acciones de edición
    })

@login_required
def obtener_prestaciones(request):
    if sin_permiso(request): return HttpResponseRedirect("/")

    servicio = request.GET.get('servicio')
    #print(f"Servicio solicitado: {servicio}")  # Log temporal
    if servicio:
        prestaciones = Prestacion.objects.filter(servicio=servicio).values('id', 'codigo', 'descripcion')
        return JsonResponse(list(prestaciones), safe=False)
    return JsonResponse([], safe=False)

@login_required
def buscar_descripcion(request):
    if sin_permiso(request): return HttpResponseRedirect("/")
        
    query = request.GET.get('q', '')
    resultados = Prestacion.objects.filter(descripcion__icontains=query).values('id', 'descripcion')[:10]
    return JsonResponse(list(resultados), safe=False)

@login_required
def nueva_prestacion(request, presupuesto_id):
    if sin_permiso(request): return HttpResponseRedirect("/")
        
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)

    # Obtener todas las prestaciones disponibles
    prestaciones = Prestacion.objects.all()

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad'))
        prestacion_id = request.POST.get('prestacion')  # ID de la prestación seleccionada
        prestacion = get_object_or_404(Prestacion, id=prestacion_id)

        # Crear un nuevo detalle de prestación
        nuevo_detalle = PresupuestoPrestacion(
            cantidad=cantidad,
            presupuesto=presupuesto,
            prestacion=prestacion
        )
        nuevo_detalle.save()
        return redirect('detalle_presupuestador')

    return render(request, 'nueva_prestacion.html', {
        'presupuesto': presupuesto,
        'prestaciones': prestaciones  # Pasar todas las prestaciones a la plantilla
    })



@login_required
def editar_presupuesto(request, numero):
    if sin_permiso(request): return HttpResponseRedirect("/")
        
    # Obtiene el presupuesto o lanza un error 404 si no existe
    presupuesto = get_object_or_404(Presupuesto, numero=numero)

    if request.method == 'POST':
        # Procesa el formulario enviado
        form = PresupuestoForm(request.POST, instance=presupuesto)
        if form.is_valid():
            form.save()  # Guarda los cambios realizados en cliente y documento
            return redirect('detalle_presupuesto', presupuesto_id=presupuesto.numero)  # Redirige a los detalles
    else:
        # Muestra el formulario con los datos actuales
        form = PresupuestoForm(instance=presupuesto)

    return render(request, 'editar_presupuesto.html', {
        'presupuesto': presupuesto,
        'form': form  # Formulario para editar el presupuesto
    })

@login_required
def importar_nomenclador(request):
    if sin_permiso(request): return HttpResponseRedirect("/")
        
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["file"]
            try:
                df = pd.read_excel(excel_file)  # Leer Excel con Pandas

                # Actualizar todos los registros a "activo" = "No"
                Prestacion.objects.exclude(codigo="999.99.99").update(activo="No")
                
                # Iterar desde la segunda línea en adelante
                for index, row in df.iterrows():
                    Prestacion.objects.create(
                        codigo=row["Codigo"],
                        descripcion=row["Descripcion"],
                        honorarios=row["Honorarios"],
                        ayudante=row["Ayudante"],
                        gastos=row["Gastos"],
                        anestesia=row["Anestesia"],
                        total=row["Total"],
                        servicio=row["Servicio"],
                        practica=row["Practica"]
                    )
                messages.success(request, "Datos importados correctamente.")
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")
        
    else:
        form = ExcelUploadForm()

    return render(request, "importar_nomenclador.html", {"form": form})


from django.db.models import Q

@login_required
def buscar_prestaciones(request):
    if sin_permiso(request): return HttpResponseRedirect("/")

    query = request.GET.get('q', '').strip()
    servicio = request.GET.get('servicio', '').strip()

    prestaciones = Prestacion.objects.filter(
        servicio=servicio
    ).filter(
        Q(descripcion__icontains=query) | Q(codigo__icontains=query)
    )[:10]
    
    results = [{
        'id': p.id,
        'codigo': p.codigo,
        'descripcion': p.descripcion,
        'precio': str(p.total or "0.00")
    } for p in prestaciones]

    return JsonResponse(results, safe=False)