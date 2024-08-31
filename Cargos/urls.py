from django.urls import path
from .views import *

urlpatterns = [
    path('cargos/', ListaCargosView.as_view(), name='lista_cargos'),
    path('cargoseditar/', ListaCargosView2.as_view(), name='lista_cargos'),
    path('crear-cargos/<int:id_usuario>/<int:id_unidad>/', CrearCargoView.as_view(), name='crear_cargo'),
    path('cargos-unidad/<int:id_usuario>/<int:id_unidad>/', ListaCargosPorUnidadView.as_view(), name='lista_cargos_por_unidad'),

]
