from django.urls import path
from .views import *

urlpatterns = [
    path('listar-orden/<int:id_usuario>/', ListarOrdenMovilizacionView.as_view(), name='listar_orden'),
    path('crear-orden/<int:id_usuario>/', CrearOrdenMovilizacionView.as_view(), name='crear_orden'),
    path('editar-orden/<int:id_orden>/', EditarOrdenMovilizacionView.as_view(), name='editar_orden'),
    path('cancelar-orden/<int:id_orden>/', CancelarOrdenMovilizacionView.as_view(), name='cancelar_orden'),
]