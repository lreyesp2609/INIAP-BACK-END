from django.urls import path
from .views import *

urlpatterns = [
    path('reporte_ordenes/<int:id_usuario>/', GenerarReporteOrdenesView.as_view(), name='reporte_ordenes'),
]
