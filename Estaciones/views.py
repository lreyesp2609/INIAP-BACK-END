from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import *
from Empleados.models import Usuarios
from django.core.exceptions import ObjectDoesNotExist

@method_decorator(csrf_exempt, name='dispatch')
class ListaCargosView(View):
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            estacion_id = request.POST.get('estacion_id')
            unidad_id = request.POST.get('unidad_id')

            cargos = Cargos.objects.filter(
                id_unidad__id_estacion=estacion_id, id_unidad=unidad_id
            ).values('id_cargo', 'cargo')

            return JsonResponse(list(cargos), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ListaEstacionesView(View):
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

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener todas las estaciones con sus datos
            estaciones = Estaciones.objects.all().values(
                'id_estacion', 
                'nombre_estacion', 
                'siglas_estacion', 
                'ruc', 
                'direccion', 
                'telefono'
            )

            return JsonResponse(list(estaciones), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
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
class ListaCargosView2(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el token del encabezado
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar y verificar el token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Si el token es válido, continuar obteniendo los cargos
            cargos = Cargos.objects.all().values('id_cargo', 'cargo')

            return JsonResponse(list(cargos), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CrearEstacionView(View):
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

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener datos del formulario FormData
            nombre_estacion = request.POST.get('nombre_estacion', '').upper()
            siglas_estacion = request.POST.get('siglas_estacion', '')

            # Generar siglas si no se proporcionan manualmente
            if not siglas_estacion:
                # Eliminar palabras comunes y convertir a siglas
                palabras_comunes = ['DE', 'LA', 'LAS', 'EL', 'LOS', 'DEL', 'Y', 'EN']
                palabras = [palabra for palabra in nombre_estacion.split() if palabra not in palabras_comunes]
                siglas_estacion = ''.join([palabra[0] for palabra in palabras]).upper()

            ruc = request.POST.get('ruc', '')
            direccion = request.POST.get('direccion', '')
            telefono = request.POST.get('telefono', '')

            # Validar campos obligatorios si es necesario
            if not nombre_estacion:
                return JsonResponse({'error': 'El nombre de la estación es requerido'}, status=400)

            # Verificar si ya existe una estación con el mismo nombre
            if Estaciones.objects.filter(nombre_estacion=nombre_estacion).exists():
                return JsonResponse({'error': 'Ya existe una estación con este nombre'}, status=400)

            # Verificar si ya existe una estación con el mismo RUC
            if ruc and Estaciones.objects.filter(ruc=ruc).exists():
                return JsonResponse({'error': 'Ya existe una estación registrada con este RUC'}, status=400)

            # Crear la estación
            estacion = Estaciones.objects.create(
                nombre_estacion=nombre_estacion,
                siglas_estacion=siglas_estacion,
                ruc=ruc,
                direccion=direccion,
                telefono=telefono
            )

            return JsonResponse({'mensaje': 'Estación creada exitosamente', 'id_estacion': estacion.id_estacion}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarEstacionView(View):
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

            # Obtener datos del formulario FormData
            nombre_estacion = request.POST.get('nombre_estacion', '').upper()

            # Generar siglas automáticamente
            palabras_comunes = ['DE', 'LA', 'LAS', 'EL', 'LOS', 'DEL', 'Y', 'EN']
            palabras = [palabra for palabra in nombre_estacion.split() if palabra not in palabras_comunes]
            siglas_estacion = ''.join([palabra[0] for palabra in palabras]).upper()

            ruc = request.POST.get('ruc', '')
            direccion = request.POST.get('direccion', '')
            telefono = request.POST.get('telefono', '')

            # Validar campos obligatorios si es necesario
            if not nombre_estacion:
                return JsonResponse({'error': 'El nombre de la estación es requerido'}, status=400)

            # Verificar si ya existe una estación con el mismo nombre
            if Estaciones.objects.filter(nombre_estacion=nombre_estacion).exclude(id_estacion=id_estacion).exists():
                return JsonResponse({'error': 'Ya existe una estación con este nombre'}, status=400)

            # Verificar si ya existe una estación con el mismo RUC
            if ruc and Estaciones.objects.filter(ruc=ruc).exclude(id_estacion=id_estacion).exists():
                return JsonResponse({'error': 'Ya existe una estación registrada con este RUC'}, status=400)

            # Actualizar la estación
            Estaciones.objects.filter(id_estacion=id_estacion).update(
                nombre_estacion=nombre_estacion,
                siglas_estacion=siglas_estacion,
                ruc=ruc,
                direccion=direccion,
                telefono=telefono
            )

            return JsonResponse({'mensaje': 'Estación actualizada exitosamente'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)