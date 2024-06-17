from django.urls import path
from .views import ListaCargosView

urlpatterns = [
    path('cargos/', ListaCargosView.as_view(), name='lista_cargos'),
]
