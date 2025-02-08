from django.urls import path
from .views import *

urlpatterns = [
    path('registrarkilometraje/<int:id_usuario>/<int:id_vehiculo>/', RegistrarKilometrajeView.as_view(), name='registrar_kilometraje'),
    path('vehiculosultimo_kilometraje/<int:id_usuario>/<int:id_vehiculo>/', UltimoKilometrajeView.as_view(), name='ultimo_kilometraje'),
    path('vehiculos_kilometraje/<int:id_usuario>/<int:id_vehiculo>/', TodosKilometrajesView.as_view(), name='ultimo_kilometraje'),
    path('gestionar_alerta/<int:id_usuario>/<int:id_vehiculo>/', GestionarAlertasMantenimientoView.as_view(), name='gestionar_alerta'),
    path('comparar_kilometraje/<int:id_vehiculo>/', CompararKilometrajeView.as_view(), name='comparar_kilometraje'),
    path('alertas/', ListarAlertasActivasView.as_view(), name='listar_alertas'),
    path('listar_detalle_alertas/<int:id_usuario>/<int:id_vehiculo>/', ListarDetalleAlertasView.as_view(), name='listar_detalle_alertas'),
    path('reporte-kilometraje/<int:id_usuario>/', (GenerarReporteKilometrajeView.as_view()), name='generar_reporte_kilometraje'),
]


