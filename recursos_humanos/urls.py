from django.urls import path
from . import views

urlpatterns = [
    path("rh-inicio", views.rh_inicio, name="rh-inicio"),
]