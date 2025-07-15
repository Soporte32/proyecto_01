from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

class MyAdminSite(AdminSite):
    def has_permission(self, request):
        es_del_grupo = request.user.groups.filter(name='Administradores').exists()
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


class PresupuestoAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista de elementos
    list_display = ('numero', 'cliente', 'documento', 'fecha', 'activo')

    # Campos que se pueden buscar
    search_fields = ('cliente', 'documento')

    # Filtros laterales
    list_filter = ('fecha', 'activo')

    # Orden por defecto
    ordering = ('-fecha',)

    # Campos agrupados en el formulario de edición
    fieldsets = (
        ("Información General", {
            'fields': ('cliente', 'documento')
        }),
        ("Datos del Presupuesto", {
            'fields': ('fecha', 'creado_por', 'eliminado_por', 'activo')
        }),
    )

    # Solo lectura para ciertos campos
    readonly_fields = ('fecha', 'creado_por', 'eliminado_por')

my_admin_site.register(Presupuesto, PresupuestoAdmin)


class PresupuestoPrestacionAdmin(admin.ModelAdmin):
    list_display = ('presupuesto_numero', 'prestacion_descripcion', 'item_activo', 'item_creado_por', 'item_eliminado_por')

    # Campos en modo solo lectura
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in self.model._meta.fields]
        return []

    # Métodos para mostrar campos relacionados
    def presupuesto_numero(self, obj):
        return obj.presupuesto.numero
    presupuesto_numero.short_description = 'Presupuesto Nº'

    def prestacion_descripcion(self, obj):
        return obj.prestacion.descripcion
    prestacion_descripcion.short_description = 'Descripción Prestación'

    def item_activo(self, obj):
        return obj.item.activo
    item_activo.short_description = 'Activo'

    def item_creado_por(self, obj):
        return obj.item.creado_por
    item_creado_por.short_description = 'Creado por'

    def item_eliminado_por(self, obj):
        return obj.item.eliminado_por
    item_eliminado_por.short_description = 'Eliminado por'

    # Opcional: impedir agregar/borrar desde el admin
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

my_admin_site.register(PresupuestoPrestacion, PresupuestoPrestacionAdmin)

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


 