from django.urls import path
from .views import *

urlpatterns = [
    path('crear-banco/<int:id_usuario>/', CrearBancoView.as_view(), name='crear_banco'),
    path('editar-banco/<int:id_usuario>/<int:id_banco>/', EditarBancoView.as_view(), name='editar_banco'),

]
