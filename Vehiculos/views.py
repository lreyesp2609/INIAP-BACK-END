from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import *
from Empleados.models import Usuarios
import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed
import re
@method_decorator(csrf_exempt, name='dispatch')
class VehiculosListView(View):
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

            vehiculos = Vehiculo.objects.filter(habilitado=1)

            vehiculos_data = []
            for vehiculo in vehiculos:
                vehiculo_data = {
                    'id_vehiculo': vehiculo.id_vehiculo,
                    'placa': vehiculo.placa,
                    'codigo_inventario': vehiculo.codigo_inventario,
                    'modelo': vehiculo.modelo,
                    'marca': vehiculo.marca,
                    'color_primario': vehiculo.color_primario,
                    'color_secundario': vehiculo.color_secundario,
                    'anio_fabricacion': vehiculo.anio_fabricacion,
                    'numero_motor': vehiculo.numero_motor,
                    'numero_chasis': vehiculo.numero_chasis,
                    'numero_matricula': vehiculo.numero_matricula,
                    'habilitado': vehiculo.habilitado,
                }
                vehiculos_data.append(vehiculo_data)

            return JsonResponse({'vehiculos': vehiculos_data})

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
class CrearVehiculoView(View):
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

            id_subcategoria_bien = request.POST.get('id_subcategoria_bien')
            placa = request.POST.get('placa')
            codigo_inventario = request.POST.get('codigo_inventario')
            modelo = request.POST.get('modelo')
            marca = request.POST.get('marca')
            color_primario = request.POST.get('color_primario')
            color_secundario = request.POST.get('color_secundario')
            anio_fabricacion = request.POST.get('anio_fabricacion')
            numero_motor = request.POST.get('numero_motor')
            numero_chasis = request.POST.get('numero_chasis')
            numero_matricula = request.POST.get('numero_matricula')

            errores = {}

            if not re.match(r'^[A-Za-z0-9]+$', placa):
                errores['placa'] = 'La placa debe contener solo letras y números.'
            placa = placa.upper()

            if not re.match(r'^[A-Za-z0-9]+$', modelo):
                errores['modelo'] = 'El modelo debe contener solo letras y números.'
            modelo = modelo.upper()

            if not re.match(r'^[A-Za-z]+$', marca):
                errores['marca'] = 'La marca debe contener solo letras.'
            marca = marca.upper()

            if not re.match(r'^[A-Za-z]+$', color_primario):
                errores['color_primario'] = 'El color primario debe contener solo letras.'
            color_primario = color_primario.upper()

            if not re.match(r'^[A-Za-z]+$', color_secundario):
                errores['color_secundario'] = 'El color secundario debe contener solo letras.'
            color_secundario = color_secundario.upper()

            if not re.match(r'^\d{4}$', anio_fabricacion) or not (1900 <= int(anio_fabricacion) <= 2099):
                errores['anio_fabricacion'] = 'El año de fabricación debe ser un año válido entre 1900 y 2099.'

            if not re.match(r'^[A-Za-z0-9]+$', numero_motor):
                errores['numero_motor'] = 'El número de motor debe contener solo letras y números.'
            numero_motor = numero_motor.upper() 

            if not re.match(r'^[A-Za-z0-9]+$', numero_chasis):
                errores['numero_chasis'] = 'El número de chasis debe contener solo letras y números.'
            numero_chasis = numero_chasis.upper()

            if not re.match(r'^\d+$', numero_matricula):
                errores['numero_matricula'] = 'El número de matrícula debe contener solo números.'

            if errores:
                return JsonResponse({'errores': errores}, status=400)

            try:
                subcategoria = SubcategoriasBienes.objects.get(id_subcategoria_bien=id_subcategoria_bien)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Subcategoría de bienes no encontrada'}, status=404)

            vehiculo = Vehiculo.objects.create(
                id_subcategoria_bien=subcategoria,
                placa=placa,
                codigo_inventario=codigo_inventario,
                modelo=modelo,
                marca=marca,
                color_primario=color_primario,
                color_secundario=color_secundario,
                anio_fabricacion=anio_fabricacion,
                numero_motor=numero_motor,
                numero_chasis=numero_chasis,
                numero_matricula=numero_matricula,
                habilitado=1
            )

            return JsonResponse({'mensaje': 'Vehículo creado exitosamente', 'id_vehiculo': vehiculo.id_vehiculo}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DeshabilitarVehiculoView(View):
    def post(self, request, id_usuario, id_vehiculo, *args, **kwargs):
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

            motivo = request.POST.get('motivo')
            if not motivo:
                return JsonResponse({'error': 'Motivo es requerido'}, status=400)

            try:
                vehiculo = Vehiculo.objects.get(id_vehiculo=id_vehiculo)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Vehículo no encontrado'}, status=404)

            if vehiculo.habilitado == 0:
                return JsonResponse({'error': 'El vehículo ya está deshabilitado'}, status=400)

            vehiculo.habilitado = 0
            vehiculo.save()

            MotivoVehiculo.objects.create(
                id_vehiculo=vehiculo,
                motivo=motivo
            )

            return JsonResponse({'mensaje': 'Vehículo deshabilitado y motivo registrado exitosamente'}, status=200)

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