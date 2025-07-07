from django.contrib import admin

# Register your models here.

from .models import Empleado, TipoEmpleado, TipoDia
from .models import Presupuesto, Prestacion, PresupuestoPrestacion

admin.site.register(Empleado)
admin.site.register(TipoEmpleado)
admin.site.register(TipoDia)

# Configuración avanzada para la administración de Presupuesto
@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista de elementos
    list_display = ('numero', 'cliente', 'documento', 'fecha')
    
    # Campos que se pueden buscar
    search_fields = ('cliente', 'documento')
    
    # Filtros laterales
    list_filter = ('fecha',)
    
    # Orden por defecto
    ordering = ('-fecha',)  # Orden descendente por fecha (los más recientes primero)
    
    # Campos que se agrupan para editar
    fieldsets = (
        ("Información General", {
            'fields': ('cliente', 'documento')
        }),
        ("Datos del Presupuesto", {
            'fields': ('fecha',)
        }),
    )

    # Solo lectura para ciertos campos
    readonly_fields = ('fecha',)

# Configuración avanzada para la administración de Prestacion
@admin.register(Prestacion)
class PrestacionAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista de elementos
    list_display = ('codigo', 'descripcion', 'activo','honorarios', 'ayudante', 'gastos', 'anestesia', 'total', 'servicio', 'practica')
    
    # Campos que se pueden buscar
    search_fields = ('codigo', 'descripcion', 'servicio', 'practica')
    
    # Filtros laterales
    list_filter = ('servicio',)
    
    # Orden por defecto
    ordering = ('servicio',)
    
    # Campos que se agrupan para editar
    fieldsets = (
        ("Información General", {
            'fields': ('codigo', 'descripcion', 'activo','servicio', 'practica')
        }),
        ("Detalles Económicos", {
            'fields': ('honorarios', 'ayudante', 'gastos', 'anestesia', 'total')
        }),
    )

@admin.register(PresupuestoPrestacion)
class PresupuestoPrestacionAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista
    list_display = ('presupuesto', 'prestacion')
    
    # Campos que se pueden buscar
    search_fields = ('presupuesto__cliente', 'prestacion__descripcion')
    
    # Filtros laterales
    list_filter = ('presupuesto', 'prestacion')
    
    # Orden por defecto
    ordering = ('presupuesto', 'prestacion')

