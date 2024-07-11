from django.urls import path
from .views import *

urlpatterns = [
    path('nuevo-empleado/<int:id_usuario>/', NuevoEmpleadoView.as_view(), name='nuevo_empleado'),
    path('lista-empleados/<int:id_usuario>/', ListaEmpleadosView.as_view(), name='lista_empleados'),
    path('editar-empleado/<int:id_usuario>/<int:id_empleado>/', EditarEmpleadoView.as_view(), name='editar_empleado'),
    path('detalle-empleado/<int:id_usuario>/<int:id_empleado>/', DetalleEmpleadoView.as_view(), name='detalle_empleado'),
    path('deshabilitar-empleado/<int:id_usuario>/<int:id_empleado>/', DeshabilitarEmpleadoView.as_view(), name='deshabilitar_empleado'),
    path('habilitar-empleado/<int:id_usuario>/<int:id_empleado>/', HabilitarEmpleadoView.as_view(), name='habilitar_empleado'),
    path('lista-empleados-deshabilitados/<int:id_usuario>/', ListaEmpleadosDeshabilitadosView.as_view(), name='lista_empleados_deshabilitados'),
    path('reset-password/<int:id_usuario>/<int:id_empleado>/', ResetPasswordView.as_view(), name='reset_password'),

]
