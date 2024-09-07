from django.urls import path
from .views import *

urlpatterns = [
    path('crear-solicitud/<int:id_usuario>/', CrearSolicitudView.as_view(), name='crear_solicitud'),
    path('listar-solicitudes/<int:id_usuario>/', ListarSolicitudesView.as_view(), name='listar_solicitudes'),
    path('listar-solicitudes-aceptadas/<int:id_usuario>/', ListarSolicitudesAceptadasView.as_view(), name='listar_solicitudes'),
    path('listar-solicitudes-canceladas/<int:id_usuario>/', ListarSolicitudesCanceladasView.as_view(), name='listar_solicitudes'),
    path('listar-motivos/', ListarMotivosView.as_view(), name='listar_motivos'),
    path('listar-provincias-ciudades/', ListarProvinciaCiudadesView.as_view(), name='listar_provincias_ciudades'),
    path('listar-datos-personales/<int:id_usuario>/', ListarDatosPersonalesView.as_view(), name='listar_datos_personales'),
    path('previsualizar-codigo-solicitud/<int:id_usuario>/', PrevisualizarCodigoSolicitudView.as_view(), name='previsualizar_codigo_solicitud'),
    path('listar-empleados/', ListarEmpleadosView.as_view(), name='listar_empleados'),
    path('listar-empleado-sesion/<int:id_usuario>/', ListarEmpleadoSesionView.as_view(), name='listar-empleado-sesion'),
    path('listar-vehiculos-habilitados/', ListarNombreVehiculosView.as_view(), name='listar_vehiculos_habilitados'),
    path('listar-bancos/', ListarBancosView.as_view(), name='listar_bancos'),
    path('listar-solicitudes-pedientes-admin/', ListarSolicitudesPendientesAdminView.as_view(), name='listar_solicitudes'),
    path('listar-solicitudes-canceladas-admin/', ListarSolicitudesCanceladasAdminView.as_view(), name='listar_solicitudes'),
    path('listar-solicitudes-aceptadas-admin/', ListarSolicitudesAceptadasAdminView.as_view(), name='listar_solicitudes'),
    path('listar-solicitud-empleado/<int:id_solicitud>/', ListarSolicitudesEmpleadoView.as_view(), name='listar_solicitud_empleado'),
    path('actualizar-solicitud/<int:id_solicitud>/', ActualizarSolicitudView.as_view(), name='actualizar-solicitud'),
    path('editar-solicitud/<int:id_solicitud>/', EditarSolicitudView.as_view(), name='editar_solicitud'),
    path('listar-solicitudes-sin-informe/<int:id_usuario>/', ListarSolicitudesAceptadasSinInformeView.as_view(), name='listar_solicitudes_sin_informe'),
    path('datos-informe/<int:id_solicitud>/', ListarDatosInformeView.as_view(), name='listar_informe'),
    path('crear-informe/<int:id_solicitud>/', CrearInformeView.as_view(), name='crear_informe'),
    path('listar-informes/<int:id_usuario>/', ListarInformesView.as_view(), name='listar_informes'),
    path('detalle-informe/<int:id_informes>/', DetalleInformeView.as_view(), name='detalle_informe'),
    path('editar-informe/<int:id_informes>/', EditarInformeView.as_view(), name='editar_informe'),
    path('informes-sin-facturas/<int:id_usuario>/', ListarInformesSinFacturasView.as_view(), name='listar_informes_sin_facturas'),
    path('crear-justificacion/<int:id_informe>/', CrearJustificacionView.as_view(), name='crear_justificacion'),
    path('listar-facturas/<int:id_usuario>/', ListarFacturaInformesView.as_view(), name='listar_facturas'),
    path('editar-justificacion/<int:id_informe>/', EditarJustificacionView.as_view(), name='editar_justificacion'),
    path('listar-detalle-facturas/<int:id_informe>/', ListarDetalleFacturasView.as_view(), name='listar_detalle_facturas'),
    path('listar-detalle-justificaciones/<int:id_informe>/', ListarDetalleJustificacionesView.as_view(), name='listar_detalle_justificaciones'),
    path('crear-motivo-cancelado/<int:id_solicitud>/', CrearMotivoCanceladoView.as_view(), name='crear_motivo_cancelado'),
    path('listar-motivos-cancelados/<int:id_solicitud>/', ListarMotivosCanceladosView.as_view(), name='listar_motivos_cancelados'),
    path('generar_pdf/<int:id_usuario>/<int:id_informe>/pdf/', GenerarPdfInformeView.as_view(), name='generar_informe_pdf'),
    path('generar_pdf_facturas/<int:id_usuario>/<int:id_informe>/pdf/', GenerarPdfFacturasView.as_view(), name='generar_facturas_pdf'),
 ]