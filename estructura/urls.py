from django.urls import path
from . import views

urlpatterns = [
    path("es-inicio", views.es_inicio, name="es-inicio"),
    path("es-calendario", views.es_calendario, name="es-calendario"),
    path("es-ver-calendario", views.es_ver_calendario, name="es-ver-calendario"),
    path("es-editar-dia", views.es_editar_dia, name="es-editar-dia"),
    path("es-importar-empleados", views.es_importar_empleados, name="es-importar-empleados"),
]