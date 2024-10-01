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
    path('Cargos/', include('Cargos.urls')),
    path('Unidades/', include('Unidades.urls')),
    path('Informes/', include('Informes.urls')),
    path('OrdenesMovilizacion/', include('OrdenesMovilizacion.urls')),
    path('Licencias/', include('Licencias.urls')),
    path('MotivosOrdenes/', include('MotivosOrdenes.urls')),
    path('Reportes/', include('Reportes.urls')),
    path('Provincias/', include('Provincias.urls')),
    path('Ciudades/', include('Ciudades.urls')),
    path('Encabezados/', include('Encabezados.urls')),
    path('Bancos/', include('Bancos.urls')),
    path('Jefes/', include('Jefes.urls')),

]
