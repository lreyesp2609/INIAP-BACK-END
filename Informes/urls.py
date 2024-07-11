from django.urls import path
from .views import *

urlpatterns = [
   
    path('crear-solicitud/<int:id_usuario>/', CrearSolicitudView.as_view(), name='crear_solicitud'),
    path('listar-solicitudes/<int:id_usuario>/', ListarSolicitudesView.as_view(), name='listar_solicitudes'),
 ]