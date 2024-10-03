from django.urls import path
from .views import *

urlpatterns = [
    path('asignar_jefe_unidad/', AsignarJefeUnidadView.as_view(), name='asignar_jefe_unidad'),
    path('asignar_director_estacion/', AsignarDirectorEstacionView.as_view(), name='asignar_director_estacion'),
]
