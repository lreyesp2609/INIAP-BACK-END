from django.urls import path
from .views import *

urlpatterns = [
    path('ciudades/<int:id_usuario>/<int:id_provincia>/', ListarCiudadesPorProvinciaView.as_view(), name='listar_ciudades_por_provincia'),
]
