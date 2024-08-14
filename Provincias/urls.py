from django.urls import path
from .views import *

urlpatterns = [
    path('crear_provincia/<int:id_usuario>/', CrearProvinciaView.as_view(), name='crear_provincia'),
    path('listar_provincias/<int:id_usuario>/', ListarProvinciasView.as_view(), name='listar_provincias'),
    path('editar_provincia/<int:id_usuario>/<int:id_provincia>/', EditarProvinciaView.as_view(), name='editar_provincia'),

]
