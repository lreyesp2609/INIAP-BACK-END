from django.urls import path
from .views import *

urlpatterns = [
    path('ciudades/<int:id_usuario>/<int:id_provincia>/', ListarCiudadesPorProvinciaView.as_view(), name='listar_ciudades_por_provincia'),
    path('crear_ciudades/<int:id_usuario>/<int:id_provincia>/', AgregarCiudadView.as_view(), name='agregar_ciudad'),
    path('editar_ciudades/<int:id_usuario>/<int:id_ciudad>/', EditarCiudadView.as_view(), name='editar_ciudad'),
]
