from django.urls import path
from .views import CrearEncabezadoView

urlpatterns = [
    path('crear_encabezado/', CrearEncabezadoView.as_view(), name='crear_encabezado'),
]
