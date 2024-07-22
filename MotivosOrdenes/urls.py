from django.urls import path
from MotivosOrdenes.views import *

urlpatterns = [
    path('crear-motivo/<int:id_usuario>/', CreateMotivoView.as_view(), name='create_motivo'),
    path('listar-motivos/<int:id_usuario>/', ListMotivosView.as_view(), name='list_motivos'),
    path('listar-motivos-deshabilitados/<int:id_usuario>/', ListMotivosDeshabilitadosView.as_view(), name='listar_motivos_deshabilitados'),
    path('editar-motivo/<int:id_usuario>/<int:id_motivo>/', EditarMotivoView.as_view(), name='edit_motivo'),
    path('deshabilitar-motivo/<int:id_usuario>/<int:id_motivo>/', DisableMotivoView.as_view(), name='disable_motivo'),
    path('habilitar-motivo/<int:id_usuario>/<int:id_motivo>/', EnableMotivoView.as_view(), name='enable_motivo'),

]
