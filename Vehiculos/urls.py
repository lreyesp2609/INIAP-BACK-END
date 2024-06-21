from django.urls import path
from .views import VehiculosListView

urlpatterns = [
    path('vehiculos/', VehiculosListView.as_view(), name='vehiculos_list'),
]
