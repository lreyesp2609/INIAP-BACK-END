from django.urls import path
from .views import *

urlpatterns = [
    path('vehiculos/<int:id_usuario>/', VehiculosListView.as_view(), name='vehiculos_list'),
    path('crear-vehiculo/<int:id_usuario>/', CrearVehiculoView.as_view(), name='crear_vehiculo'),
]
