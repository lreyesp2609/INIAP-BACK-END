from django.urls import path
from .views import ListaCategoriasBienesView

urlpatterns = [
    path('categorias-bienes/<int:id_usuario>/', ListaCategoriasBienesView.as_view(), name='lista-categorias-bienes'),
]
