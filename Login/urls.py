from django.urls import path
from .views import *

urlpatterns = [
    path('iniciar_sesion/', IniciarSesionView.as_view(), name='iniciar_sesion'),
    path('cerrar_sesion/', CerrarSesionView.as_view(), name='cerrar_sesion'),
    path('obtener_usuario/<int:id_usuario>/', ObtenerUsuarioView.as_view(), name='obtener_usuario'),
    path('cambiar-contrasenia/<int:id_usuario>/', CambiarContraseniaView.as_view(), name='cambiar_contrasenia'),

]
