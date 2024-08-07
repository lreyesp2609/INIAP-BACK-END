from django.urls import path
from .views import *

urlpatterns = [
    path('crear-tipo-licencia/<int:id_usuario>/', CrearTipoLicenciaView.as_view(), name='crear_tipo_licencia'),
    path('listar-tipos/<int:id_usuario>/', ListarTiposLicenciasView.as_view(), name='listar_tipos_licencias'),
    path('editar-tipo-licencia/<int:id_usuario>/<int:id_tipo_licencia>/', EditarTipoLicenciaView.as_view(), name='editar_tipo_licencia'),

]
