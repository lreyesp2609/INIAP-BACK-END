from django.urls import path
from .views import ObtenerRolesView

urlpatterns = [
    path('roles/', ObtenerRolesView.as_view(), name='obtener_roles'),
]
