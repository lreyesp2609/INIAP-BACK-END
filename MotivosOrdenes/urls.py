from django.urls import path
from MotivosOrdenes.views import *

urlpatterns = [
    path('crear-motivo/<int:id_usuario>/', CreateMotivoView.as_view(), name='create_motivo'),
    path('listar-motivos/<int:id_usuario>/', ListMotivosView.as_view(), name='list_motivos'),

]
