from django.urls import path
from . import views


urlpatterns = [
    path('presupuesto/nuevo/', views.presupuesto_nuevo, name='presupuesto_nuevo'),
    path('nueva_prestacion/<int:presupuesto_id>/', views.nueva_prestacion, name='nueva_prestacion'),
    path('buscar_descripcion/', views.buscar_descripcion, name='buscar_descripcion'),
    path('importar_nomenclador/', views.importar_nomenclador, name='importar_nomenclador'),
    path('detalle_presupuestador/', views.detalle_presupuestador, name='detalle_presupuestador'),
    path('presupuesto/<int:presupuesto_id>/agregar_item/', views.agregar_item, name='agregar_item'),
    path('presupuesto/<int:presupuesto_id>/eliminar_item/', views.eliminar_item, name='eliminar_item'),
    path('obtener-prestaciones/', views.obtener_prestaciones, name='obtener_prestaciones'),
    path('presupuesto/<int:presupuesto_id>/detalle/', views.detalle_presupuesto, name='detalle_presupuesto'),
    path('presupuesto/<int:numero>/editar/', views.editar_presupuesto, name='editar_presupuesto'),
    path('buscar-prestaciones/', views.buscar_prestaciones, name='buscar_prestaciones'),
    path('presupuestos/<int:presupuesto_id>/eliminar/', views.presupuesto_eliminar, name='presupuesto_eliminar'),

]
