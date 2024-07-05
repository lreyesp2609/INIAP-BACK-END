from django.urls import path
from .views import *

urlpatterns = [
    path('cargos/', ListaCargosView.as_view(), name='lista_cargos'),
    path('cargoseditar/', ListaCargosView2.as_view(), name='lista_cargos'),
    path('estaciones/<int:id_usuario>/', ListaEstacionesView.as_view(), name='lista_estaciones'),
    path('unidades/', ListaUnidadesPorEstacionView.as_view(), name='lista_unidades'),
    path('crear-estacion/<int:id_usuario>/', CrearEstacionView.as_view(), name='crear_estacion'),
    path('editar-estacion/<int:id_usuario>/<int:id_estacion>/', EditarEstacionView.as_view(), name='editar-estacion'),

]
