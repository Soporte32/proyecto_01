from django.urls import path
from . import views

urlpatterns = [
    path("rh-inicio", views.rh_inicio, name="rh-inicio"),
    path("solicitar-horas-samic/", views.solicitar_horas_samic, name="solicitar-horas-samic"),
]