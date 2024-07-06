from django.urls import path
from .views import *

urlpatterns = [
    path('estaciones/<int:id_usuario>/', ListaEstacionesView.as_view(), name='lista_estaciones'),
    path('crear-estacion/<int:id_usuario>/', CrearEstacionView.as_view(), name='crear_estacion'),
    path('editar-estacion/<int:id_usuario>/<int:id_estacion>/', EditarEstacionView.as_view(), name='editar-estacion'),
]
