from django.urls import path
from .views import *

urlpatterns = [
    path('listar-orden/<int:id_usuario>/', ListarOrdenMovilizacionView.as_view(), name='listar_orden'),
    path('crear-orden/<int:id_usuario>/', CrearOrdenMovilizacionView.as_view(), name='crear_orden'),
    path('editar-orden/<int:id_usuario>/<int:id_orden>/', EditarOrdenMovilizacionView.as_view(), name='editar_orden'),
    path('detalle-orden/<int:id_usuario>/<int:id_orden>/', DetalleOrdenMovilizacion.as_view(), name='detalle_orden'),
    path('cancelar-orden/<int:id_usuario>/<int:id_orden>/', CancelarOrdenMovilizacionView.as_view(), name='cancelar_orden'),
    path('habilitar-orden/<int:id_usuario>/<int:id_orden>/', HabilitarOrdenMovilizacionView.as_view(), name='habilitar_orden'),
    path('listar-todas-orden/<int:id_usuario>/', ListarTodasOrdenMovilizacionView.as_view(), name='listar-todas-orden'),
    path('aprobar-orden/<int:id_usuario>/<int:id_orden>/', AprobarOrdenMovilizacionView.as_view(), name='aprobar_orden'),
    path('rechazar-orden/<int:id_usuario>/<int:id_orden>/', RechazarOrdenMovilizacionView.as_view(), name='rechazar_orden'),
    path('listar-motivos/<int:id_usuario>/', ListarMotivoOrdenesMovilizacionView.as_view(), name='listar_motivos'),
    path('editar-motivo/<int:id_usuario>/<int:id_orden>/<int:id_motivo>/', EditarMotivoOrdenMovilizacionView.as_view(), name='editar_motivo'),
    path('generar-pdf/<int:id_usuario>/<int:id_orden>/pdf/', GenerarPdfOrdenMovilizacionView.as_view(), name='generar_pdf'),
    path('listar-ordenes-aprobadas/<int:id_usuario>/', ListarOrdenesAprobadasView.as_view(), name='listar_ordenes_aprobadas'),
    path('editar-horario/<int:id_usuario>/', EditarHorarioView.as_view(), name='editar_horario'),
    path('crear-ruta/<int:id_usuario>/', CrearRutaView.as_view(), name='editar_horario'),
    path('ver-horario/<int:id_usuario>/', VerHorarioView.as_view(), name='ver_horario'),
    path('editar-ruta/<int:id_usuario>/<int:id_ruta_movilizacion>/', EditarRutaView.as_view(), name='editar_horario'),
    path('listar-rutas/<int:id_usuario>/', ListarRutasView.as_view(), name='listar_rutas'),
    path('cambiar-estado-rutas/<int:id_usuario>/<int:id_ruta_movilizacion>/', CambiarEstadoRutaView.as_view(), name='cambiar_estado_ruta'),
]