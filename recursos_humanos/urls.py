from django.urls import path
from . import views

urlpatterns = [
    path("rh-inicio", views.rh_inicio, name="rh-inicio"),
    path("solicitar-horas-samic/", views.solicitar_horas_samic, name="solicitar-horas-samic"),
    path('autorizar-horas-samic/', views.autorizar_horas_samic, name='autorizar-horas-samic'),
    path('accion-horas-samic/<int:solicitud_id>/', views.accion_horas_samic, name='accion-horas-samic'),

]