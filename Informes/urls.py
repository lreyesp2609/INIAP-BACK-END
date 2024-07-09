from django.urls import path
from .views import *

urlpatterns = [
   
 path('generar-numero-solicitud/<int:id_solicitud>/', generar_numero_solicitud, name='generar_numero_solicitud'),
 path('crear-solicitud-informe/<int:id_usuario>/', crear_solicitud_informe, name='crear_solicitud_informe'),
 path('listar-solicitudes/<int:id_usuario>/', listar_solicitudes, name='listar_solicitudes'),
 ]
