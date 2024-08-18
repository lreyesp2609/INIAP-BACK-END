from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import *
import jwt
from django.conf import settings

@method_decorator(csrf_exempt, name='dispatch')
class ListarCiudadesPorProvinciaView(View):
    @transaction.atomic
    def get(self, request, id_usuario, id_provincia, *args, **kwargs):
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

            # Verificar si la provincia existe
            if not Provincias.objects.filter(id_provincia=id_provincia).exists():
                return JsonResponse({'error': 'Provincia no encontrada'}, status=404)

            # Obtener las ciudades de la provincia ordenadas por id_ciudad de menor a mayor
            ciudades = Ciudades.objects.filter(id_provincia=id_provincia).order_by('id_ciudad').values('id_ciudad', 'ciudad')

            return JsonResponse(list(ciudades), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AgregarCiudadView(View):
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

            # Verificar si la provincia existe
            if not Provincias.objects.filter(id_provincia=id_provincia).exists():
                return JsonResponse({'error': 'Provincia no encontrada'}, status=404)

            # Obtener el nombre de la ciudad del formulario y convertir a mayúsculas
            ciudad = request.POST.get('ciudad')
            if not ciudad:
                return JsonResponse({'error': 'Nombre de la ciudad no proporcionado'}, status=400)

            ciudad = ciudad.upper()

            # Crear la nueva ciudad
            nueva_ciudad = Ciudades(id_provincia_id=id_provincia, ciudad=ciudad)
            nueva_ciudad.save()

            return JsonResponse({'message': 'Ciudad agregada correctamente'}, status=201)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarCiudadView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_ciudad, *args, **kwargs):
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

            # Verificar si la ciudad existe
            ciudad = Ciudades.objects.filter(id_ciudad=id_ciudad).first()
            if not ciudad:
                return JsonResponse({'error': 'Ciudad no encontrada'}, status=404)

            # Obtener los datos de la ciudad del formulario y convertir a mayúsculas
            form_data = request.POST
            nuevo_nombre = form_data.get('ciudad')
            if not nuevo_nombre:
                return JsonResponse({'error': 'Nombre de la ciudad no proporcionado'}, status=400)

            nuevo_nombre = nuevo_nombre.upper()

            # Actualizar la ciudad
            ciudad.ciudad = nuevo_nombre
            ciudad.save()

            return JsonResponse({'message': 'Ciudad actualizada correctamente'}, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)
