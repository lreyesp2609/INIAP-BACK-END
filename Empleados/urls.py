from django.urls import path
from .views import *

urlpatterns = [
    path('nuevo-empleado/<int:id_usuario>/', NuevoEmpleadoView.as_view(), name='nuevo_empleado'),
    path('lista-empleados/<int:id_usuario>/', ListaEmpleadosView.as_view(), name='lista_empleados'),
]
