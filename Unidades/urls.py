from django.urls import path
from .views import *

urlpatterns = [
    path('unidades/', ListaUnidadesPorEstacionView.as_view(), name='lista_unidades'),
    path('crear-unidades/<int:id_usuario>/<int:id_estacion>/', CrearUnidadView.as_view(), name='crear_unidad'),
]
