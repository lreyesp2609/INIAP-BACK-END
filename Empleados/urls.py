from django.urls import path
from .views import NuevoEmpleadoView

urlpatterns = [
    path('nuevo-empleado/<int:id_usuario>/', NuevoEmpleadoView.as_view(), name='nuevo_empleado'),
]
