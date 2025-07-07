from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView
from proyecto_01.views import dashboard
from estructura.admin import my_admin_site

urlpatterns = [
    path('admin/', my_admin_site.urls),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', dashboard),
    path("estructura/", include("estructura.urls")),
    path("presupuestador/", include("presupuestador.urls")),
    path("recursoshumanos/", include("recursos_humanos.urls")),
]
