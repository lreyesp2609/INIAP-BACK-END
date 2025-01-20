from django.urls import path
from .views import *

urlpatterns = [
    path('reporte_ordenes/<int:id_usuario>/', GenerarReporteOrdenesView.as_view(), name='reporte_ordenes'),
    path('reporte_informes/<int:id_usuario>/', GenerarReporteInformeViajesView.as_view(), name='reporte_ordenes'),
    path('reporte_facturas/<int:id_usuario>/', GenerarReporteInformeFacturasView.as_view(), name='reporte_ordenes'),
]
