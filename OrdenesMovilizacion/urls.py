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
    path('editar-motivo/<int:id_usuario>/<int:id_motivo>/', EditarMotivoOrdenMovilizacionView.as_view(), name='editar_motivo'),
    path('editar-secuencial/<int:id_usuario>/<int:id_orden>/', EditarSecuencialOrdenMovilizacionView.as_view(), name='editar_secuencial'),
]