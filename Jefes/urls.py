from django.urls import path
from .views import AsignarJefeUnidadView

urlpatterns = [
    path('asignar_jefe_unidad/', AsignarJefeUnidadView.as_view(), name='asignar_jefe_unidad'),
]
