from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import *
from Empleados.models import Usuarios

@method_decorator(csrf_exempt, name='dispatch')
class ListaCategoriasBienesView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener todas las categorías de bienes
            categorias_bienes = CategoriasBienes.objects.all()

            categorias_list = []
            for categoria in categorias_bienes:
                categoria_data = {
                    'id_categorias_bien': categoria.id_categorias_bien,
                    'descripcion_categoria': categoria.descripcion_categoria,
                    'subcategorias': []
                }
                
                # Obtener todas las subcategorías de esta categoría específica
                subcategorias = SubcategoriasBienes.objects.filter(id_categorias_bien=categoria.id_categorias_bien)
                for subcategoria in subcategorias:
                    subcategoria_data = {
                        'id_subcategoria_bien': subcategoria.id_subcategoria_bien,
                        'descripcion': subcategoria.descripcion,
                        'identificador': subcategoria.identificador
                    }
                    categoria_data['subcategorias'].append(subcategoria_data)

                categorias_list.append(categoria_data)

            return JsonResponse(categorias_list, safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
