from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from Empleados.models import Usuarios
from .models import *

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class ListaUnidadesPorEstacionView(View):
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            estacion_id = request.POST.get('estacion_id')
            if not estacion_id:
                return JsonResponse({'error': 'ID de estación no proporcionado'}, status=400)

            unidades = Unidades.objects.filter(id_estacion=estacion_id).values('id_unidad', 'nombre_unidad', 'id_estacion_id')

            return JsonResponse(list(unidades), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CrearUnidadView(View):
    def post(self, request, id_usuario, id_estacion, *args, **kwargs):
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

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            nombre_unidad = request.POST.get('nombre_unidad')

            # Función para generar siglas excluyendo palabras comunes
            def generar_siglas(nombre):
                palabras_comunes = ['DE', 'LA', 'LAS', 'EL', 'LOS', 'DEL', 'Y', 'EN']
                palabras = [palabra.upper() for palabra in nombre.split() if palabra.upper() not in palabras_comunes]
                siglas = ''.join(palabra[0] for palabra in palabras)
                return siglas[:3]  # Tomar solo las primeras tres letras

            siglas_unidad = generar_siglas(nombre_unidad)

            if not nombre_unidad:
                return JsonResponse({'error': 'Nombre de la unidad no proporcionado'}, status=400)

            # Verificar si la estación existe
            try:
                estacion = Estaciones.objects.get(id_estacion=id_estacion)
            except Estaciones.DoesNotExist:
                return JsonResponse({'error': 'Estación no encontrada'}, status=404)

            # Crear la nueva unidad
            nueva_unidad = Unidades(
                nombre_unidad=nombre_unidad,
                siglas_unidad=siglas_unidad,
                id_estacion=estacion
            )
            nueva_unidad.save()

            return JsonResponse({
                'id_unidad': nueva_unidad.id_unidad,
                'nombre_unidad': nueva_unidad.nombre_unidad,
                'siglas_unidad': nueva_unidad.siglas_unidad,
                'id_estacion': nueva_unidad.id_estacion.id_estacion
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
