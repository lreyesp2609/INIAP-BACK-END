from django.contrib import admin
from django.urls import path
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Login/', include('Login.urls')),
    path('Empleados/', include('Empleados.urls')),
    path('Estaciones/', include('Estaciones.urls')),
    path('Roles/', include('Roles.urls')),
    path('Vehiculos/', include('Vehiculos.urls')),
    path('CategoriasBienes/', include('CategoriasBienes.urls')),
]
