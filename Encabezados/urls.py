from django.urls import path
from .views import *

urlpatterns = [
    path('crear_encabezado/', CrearEncabezadoView.as_view(), name='crear_encabezado'),
    path('obtener_encabezado/', ObtenerEncabezadoView.as_view(), name='obtener_encabezado'),
]
