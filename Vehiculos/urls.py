from django.urls import path
from .views import *

urlpatterns = [
    path('vehiculos/<int:id_usuario>/', VehiculosListView.as_view(), name='vehiculos_list'),
    path('crear-vehiculo/<int:id_usuario>/', CrearVehiculoView.as_view(), name='crear_vehiculo'),
    path('deshabilitar-vehiculo/<int:id_usuario>/<int:id_vehiculo>/', DeshabilitarVehiculoView.as_view(), name='deshabilitar_vehiculo'),
    path('habilitar-vehiculo/<int:id_usuario>/<int:id_vehiculo>/', HabilitarVehiculoView.as_view(), name='habilitar_vehiculo'),
    path('vehiculosdeshabilitados/<int:id_usuario>/', VehiculosListViewDeshabilitados.as_view(), name='vehiculos_list'),
    path('editar-vehiculo/<int:id_usuario>/<int:id_vehiculo>/', ModificarVehiculoView.as_view(), name='modificar_vehiculo'),
    path('detalle-vehiculo/<int:id_usuario>/<int:id_vehiculo>/', DetalleVehiculoView.as_view(), name='detalle_vehiculo'),
]
