import re
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import jwt
from django.conf import settings
from Empleados.models import Usuarios
from Provincias.models import Provincias

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class CrearProvinciaView(View):
    @transaction.atomic
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expirado'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Token inválido'}, status=401)

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            nombre_provincia = request.POST.get('provincia')

            if not nombre_provincia:
                return JsonResponse({'error': 'Nombre de la provincia no proporcionado'}, status=400)

            # Validación del nombre de la provincia
            if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', nombre_provincia):
                return JsonResponse({'error': 'El nombre de la provincia debe contener solo letras y espacios.'}, status=400)

            nombre_provincia = nombre_provincia.upper()

            # Verificar si ya existe una provincia con el mismo nombre
            if Provincias.objects.filter(provincia=nombre_provincia).exists():
                return JsonResponse({'error': 'Ya existe una provincia con el mismo nombre.'}, status=400)

            # Crear la nueva provincia
            nueva_provincia = Provincias(provincia=nombre_provincia)
            nueva_provincia.save()

            return JsonResponse({
                'id_provincia': nueva_provincia.id_provincia,
                'provincia': nueva_provincia.provincia
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListarProvinciasView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expirado'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Token inválido'}, status=401)

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Ordenar las provincias por id_provincia de menor a mayor
            provincias = Provincias.objects.all().order_by('id_provincia').values('id_provincia', 'provincia')

            return JsonResponse(list(provincias), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class EditarProvinciaView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_provincia, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expirado'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Token inválido'}, status=401)

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            nombre_provincia = request.POST.get('provincia')

            if not nombre_provincia:
                return JsonResponse({'error': 'Nombre de la provincia no proporcionado'}, status=400)

            # Validación del nombre de la provincia
            if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', nombre_provincia):
                return JsonResponse({'error': 'El nombre de la provincia debe contener solo letras y espacios.'}, status=400)

            nombre_provincia = nombre_provincia.upper()

            # Verificar si ya existe una provincia con el mismo nombre
            if Provincias.objects.filter(provincia=nombre_provincia).exclude(id_provincia=id_provincia).exists():
                return JsonResponse({'error': 'Ya existe una provincia con el mismo nombre.'}, status=400)

            # Editar la provincia existente
            provincia = Provincias.objects.get(id_provincia=id_provincia)
            provincia.provincia = nombre_provincia
            provincia.save()

            return JsonResponse({
                'id_provincia': provincia.id_provincia,
                'provincia': provincia.provincia
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Provincias.DoesNotExist:
            return JsonResponse({'error': 'Provincia no encontrada'}, status=404)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)