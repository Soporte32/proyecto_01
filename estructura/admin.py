from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

class MyAdminSite(AdminSite):
    def has_permission(self, request):
        es_del_grupo = request.user.groups.filter(name='administrador').exists()
        es_usuario_administrador = request.user.username == 'administrador'

        return request.user.is_active and request.user.is_authenticated and (es_del_grupo or es_usuario_administrador)

my_admin_site = MyAdminSite(name='myadmin')

my_admin_site.register(User, UserAdmin)
my_admin_site.register(Group)

from .models import Empleado, TipoEmpleado, TipoDia
from .models import Presupuesto, Prestacion, PresupuestoPrestacion

my_admin_site.register(Empleado)
my_admin_site.register(TipoEmpleado)
my_admin_site.register(TipoDia)

# Configuración avanzada para la administración de Presupuesto
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

my_admin_site.register(Presupuesto, PresupuestoAdmin)


# Configuración avanzada para la administración de Prestacion
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

my_admin_site.register(Prestacion, PrestacionAdmin)    


class PresupuestoPrestacionAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista
    list_display = ('presupuesto', 'prestacion')
    
    # Campos que se pueden buscar
    search_fields = ('presupuesto__cliente', 'prestacion__descripcion')
    
    # Filtros laterales
    list_filter = ('presupuesto', 'prestacion')
    
    # Orden por defecto
    ordering = ('presupuesto', 'prestacion')

my_admin_site.register(PresupuestoPrestacion, PresupuestoPrestacionAdmin)   