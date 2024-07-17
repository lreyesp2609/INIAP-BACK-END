from django.urls import path
from .views import *

urlpatterns = [
   
    path('crear-solicitud/<int:id_usuario>/', CrearSolicitudView.as_view(), name='crear_solicitud'),
    path('listar-solicitudes/<int:id_usuario>/', ListarSolicitudesView.as_view(), name='listar_solicitudes'),
    path('listar-bancos/', ListarBancosView.as_view(), name='listar_bancos'),
    path('listar-motivos/', ListarMotivosView.as_view(), name='listar_motivos'),
    path('listar-provincias-ciudades/', ListarProvinciaCiudadesView.as_view(), name='listar_provincias_ciudades'),
    path('listar-datos-personales/<int:id_usuario>/', ListarDatosPersonalesView.as_view(), name='listar_datos_personales'),
    path('previsualizar-codigo-solicitud/<int:id_usuario>/', PrevisualizarCodigoSolicitudView.as_view(), name='previsualizar_codigo_solicitud'),
    path('listar-empleados/', ListarEmpleadosView.as_view(), name='listar_empleados'),
    path('listar-empleado-sesion/<int:id_usuario>/', ListarEmpleadoSesion.as_view(), name='listar-empleado-sesion'),
 ]