from django.urls import path
from .views import *

urlpatterns = [
    path('registrarkilometraje/<int:id_usuario>/<int:id_vehiculo>/', RegistrarKilometrajeView.as_view(), name='registrar_kilometraje'),
    path('vehiculosultimo_kilometraje/<int:id_usuario>/<int:id_vehiculo>/', UltimoKilometrajeView.as_view(), name='ultimo_kilometraje'),
    path('vehiculos_kilometraje/<int:id_usuario>/<int:id_vehiculo>/', TodosKilometrajesView.as_view(), name='ultimo_kilometraje'),

]
