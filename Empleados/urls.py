from django.urls import path
from .views import *

urlpatterns = [
    path('nuevo-empleado/<int:id_usuario>/', NuevoEmpleadoView.as_view(), name='nuevo_empleado'),
    path('lista-empleados/<int:id_usuario>/', ListaEmpleadosView.as_view(), name='lista_empleados'),
    path('editar-empleado/<int:id_usuario>/<int:id_empleado>/', EditarEmpleadoView.as_view(), name='editar_empleado'),
    path('detalle-empleado/<int:id_usuario>/<int:id_empleado>/', DetalleEmpleadoView.as_view(), name='detalle_empleado'),

]
