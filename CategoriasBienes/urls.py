from django.urls import path
from .views import *

urlpatterns = [
    path('categorias-bienes/<int:id_usuario>/', ListaCategoriasBienesView.as_view(), name='lista-categorias-bienes'),
    path('crear_categoria/<int:id_usuario>/', CrearCategoriaBienesView.as_view(), name='crear_categoria'),
    path('crear_subcategoria/<int:id_usuario>/<int:id_categorias_bien>/', CrearSubcategoriaBienesView.as_view(), name='crear_subcategoria'),
    path('subcategorias/<int:id_categoria>/', ListaSubcategoriasPorCategoriaView.as_view(), name='listar_subcategorias_por_categoria'),
]
