from django.urls import path
from .views import *

urlpatterns = [
    path('reporte_ordenes/<int:id_usuario>/', GenerarReporteView.as_view(), name='reporte_ordenes'),
]
