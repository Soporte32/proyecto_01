from django.urls import path
from . import views

urlpatterns = [
    path("rh-inicio", views.rh_inicio, name="rh-inicio"),
    path("solicitar-horas-samic/", views.solicitar_horas_samic, name="solicitar-horas-samic"),
    path('autorizar-horas-samic/', views.autorizar_horas_samic, name='autorizar-horas-samic'),
    path('accion-horas-samic/<int:solicitud_id>/', views.accion_horas_samic, name='accion-horas-samic'),
    path('anular-horas-samic/', views.anular_solicitudes_form, name='anular-horas-samic'),
    path('accion-anular-horas-samic/<int:solicitud_id>/', views.accion_anular_horas_samic, name='accion-anular-horas-samic'),
    path('mis-horas-samic/', views.mis_horas_samic, name='mis-horas-samic'),

]