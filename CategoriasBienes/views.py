import re
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import *
from Empleados.models import Usuarios
from django.db import transaction

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

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener todas las categorías de bienes ordenadas de menor a mayor
            categorias_bienes = CategoriasBienes.objects.all().order_by('id_categorias_bien')

            categorias_list = []
            for categoria in categorias_bienes:
                categoria_data = {
                    'id_categorias_bien': categoria.id_categorias_bien,
                    'descripcion_categoria': categoria.descripcion_categoria,
                    'subcategorias': []
                }
                
                # Obtener todas las subcategorías de esta categoría específica ordenadas de menor a mayor
                subcategorias = SubcategoriasBienes.objects.filter(id_categorias_bien=categoria.id_categorias_bien).order_by('id_subcategoria_bien')
                for subcategoria in subcategorias:
                    subcategoria_data = {
                        'id_subcategoria_bien': subcategoria.id_subcategoria_bien,
                        'descripcion': subcategoria.descripcion,
                        'identificador': subcategoria.identificador
                    }
                    categoria_data['subcategorias'].append(subcategoria_data)

                categorias_list.append(categoria_data)

            # Ordenar la lista de categorías en el orden correcto
            categorias_list = sorted(categorias_list, key=lambda x: x['id_categorias_bien'])

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

@method_decorator(csrf_exempt, name='dispatch')
class CrearCategoriaBienesView(View):
    @transaction.atomic
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener la descripción de la categoría del formulario
            descripcion_categoria = request.POST.get('descripcion_categoria')
            if not descripcion_categoria:
                return JsonResponse({'error': 'Descripción de categoría no proporcionada'}, status=400)

            # Validar que la descripción solo contenga texto, incluyendo letras con tildes y espacios
            if not isinstance(descripcion_categoria, str) or not re.match(r"^[\w\sáéíóúüñÁÉÍÓÚÜÑ]+$", descripcion_categoria):
                return JsonResponse({'error': 'La descripción de la categoría solo debe contener letras, tildes, espacios y caracteres especiales'}, status=400)

            # Convertir la descripción a mayúsculas
            descripcion_categoria = descripcion_categoria.upper()

            # Crear la nueva categoría de bienes
            nueva_categoria = CategoriasBienes.objects.create(descripcion_categoria=descripcion_categoria)

            return JsonResponse({
                'id_categorias_bien': nueva_categoria.id_categorias_bien,
                'descripcion_categoria': nueva_categoria.descripcion_categoria
            }, status=201)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Exception as e:
            transaction.set_rollback(True)  # Asegurar rollback en caso de excepción
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CrearSubcategoriaBienesView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_categorias_bien, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener los datos del formulario
            descripcion = request.POST.get('descripcion')
            identificador = request.POST.get('identificador')

            if not descripcion:
                return JsonResponse({'error': 'Descripción no proporcionada'}, status=400)
            if not identificador:
                return JsonResponse({'error': 'Identificador no proporcionado'}, status=400)

            # Validar que la descripción solo contenga texto
            if not isinstance(descripcion, str) or not re.match(r"^[a-zA-Z\s]+$", descripcion):
                return JsonResponse({'error': 'La descripción solo debe contener letras y espacios'}, status=400)

            # Validar que el identificador solo contenga números
            if not identificador.isdigit():
                return JsonResponse({'error': 'El identificador solo debe contener números'}, status=400)

            # Convertir la descripción a mayúsculas
            descripcion = descripcion.upper()

            # Verificar que la categoría de bienes exista
            if not CategoriasBienes.objects.filter(id_categorias_bien=id_categorias_bien).exists():
                return JsonResponse({'error': 'Categoría de bienes no encontrada'}, status=404)

            # Crear la nueva subcategoría de bienes
            nueva_subcategoria = SubcategoriasBienes.objects.create(
                id_categorias_bien_id=id_categorias_bien,
                descripcion=descripcion,
                identificador=identificador
            )

            return JsonResponse({
                'id_subcategoria_bien': nueva_subcategoria.id_subcategoria_bien,
                'id_categorias_bien': nueva_subcategoria.id_categorias_bien_id,
                'descripcion': nueva_subcategoria.descripcion,
                'identificador': nueva_subcategoria.identificador
            }, status=201)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Exception as e:
            transaction.set_rollback(True)  # Asegurar rollback en caso de excepción
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListaSubcategoriasPorCategoriaView(View):
    def get(self, request, id_categoria, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener subcategorías por id de categoría
            subcategorias = SubcategoriasBienes.objects.filter(id_categorias_bien=id_categoria)
            subcategorias_list = []
            for subcategoria in subcategorias:
                subcategoria_data = {
                    'id_subcategoria_bien': subcategoria.id_subcategoria_bien,
                    'descripcion': subcategoria.descripcion,
                    'identificador': subcategoria.identificador
                }
                subcategorias_list.append(subcategoria_data)

            return JsonResponse(subcategorias_list, safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarCategoriaBienesView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_categoria_bien, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener la descripción de la categoría del formulario
            descripcion_categoria = request.POST.get('descripcion_categoria')
            if not descripcion_categoria:
                return JsonResponse({'error': 'Descripción de categoría no proporcionada'}, status=400)

            # Validar que la descripción solo contenga texto, incluyendo letras con tildes y espacios
            if not isinstance(descripcion_categoria, str) or not re.match(r"^[\w\sáéíóúüñÁÉÍÓÚÜÑ]+$", descripcion_categoria):
                return JsonResponse({'error': 'La descripción de la categoría solo debe contener letras, tildes, espacios y caracteres especiales'}, status=400)

            # Convertir la descripción a mayúsculas
            descripcion_categoria = descripcion_categoria.upper()

            # Editar la categoría de bienes existente
            categoria_bien = CategoriasBienes.objects.get(id_categorias_bien=id_categoria_bien)
            categoria_bien.descripcion_categoria = descripcion_categoria
            categoria_bien.save()

            return JsonResponse({
                'id_categorias_bien': categoria_bien.id_categorias_bien,
                'descripcion_categoria': categoria_bien.descripcion_categoria
            }, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except CategoriasBienes.DoesNotExist:
            return JsonResponse({'error': 'Categoría de bienes no encontrada'}, status=404)

        except Exception as e:
            transaction.set_rollback(True)  # Asegurar rollback en caso de excepción
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarSubcategoriaBienesView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_categoria, id_subcategoria, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener la descripción de la subcategoría y el identificador del formulario
            descripcion_subcategoria = request.POST.get('descripcion')
            identificador = request.POST.get('identificador')

            if not descripcion_subcategoria:
                return JsonResponse({'error': 'Descripción de subcategoría no proporcionada'}, status=400)

            # Validar que la descripción solo contenga texto, incluyendo letras con tildes y espacios
            if not isinstance(descripcion_subcategoria, str) or not re.match(r"^[\w\sáéíóúüñÁÉÍÓÚÜÑ]+$", descripcion_subcategoria):
                return JsonResponse({'error': 'La descripción de la subcategoría solo debe contener letras, tildes, espacios y caracteres especiales'}, status=400)

            # Convertir la descripción a mayúsculas
            descripcion_subcategoria = descripcion_subcategoria.upper()

            # Editar la subcategoría existente
            subcategoria = SubcategoriasBienes.objects.get(id_subcategoria_bien=id_subcategoria, id_categorias_bien=id_categoria)
            subcategoria.descripcion = descripcion_subcategoria

            # Solo actualizar el identificador si se ha proporcionado uno nuevo
            if identificador:
                subcategoria.identificador = identificador

            subcategoria.save()

            return JsonResponse({
                'id_subcategoria_bien': subcategoria.id_subcategoria_bien,
                'descripcion': subcategoria.descripcion,
                'identificador': subcategoria.identificador
            }, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except SubcategoriasBienes.DoesNotExist:
            return JsonResponse({'error': 'Subcategoría no encontrada'}, status=404)

        except Exception as e:
            transaction.set_rollback(True)  # Asegurar rollback en caso de excepción
            return JsonResponse({'error': str(e)}, status=500)
