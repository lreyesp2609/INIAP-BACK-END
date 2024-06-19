from django.urls import path
from .views import *

urlpatterns = [
    path('cargos/', ListaCargosView.as_view(), name='lista_cargos'),
    path('cargoseditar/', ListaCargosView2.as_view(), name='lista_cargos'),
    path('estaciones/', ListaEstacionesView.as_view(), name='lista_estaciones'),
    path('unidades/', ListaUnidadesPorEstacionView.as_view(), name='lista_unidades'),
]
