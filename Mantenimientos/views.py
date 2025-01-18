from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from Mantenimientos.models import *
from Vehiculos.models import *
import jwt
from django.conf import settings
import re

@method_decorator(csrf_exempt, name='dispatch')
class RegistrarKilometrajeView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_vehiculo, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token
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

            # Validar que el vehículo existe
            try:
                vehiculo = Vehiculo.objects.get(id_vehiculo=id_vehiculo)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Vehículo no encontrado'}, status=404)

            # Obtener datos del POST
            fecha_registro = request.POST.get('fecha_registro')
            kilometraje = request.POST.get('kilometraje')
            evento = request.POST.get('evento')

            # Validaciones de los datos
            errores = {}
            if not fecha_registro or not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_registro):
                errores['fecha_registro'] = 'La fecha debe tener el formato YYYY-MM-DD.'

            if not kilometraje or not kilometraje.isdigit() or int(kilometraje) < 0:
                errores['kilometraje'] = 'El kilometraje debe ser un número entero positivo.'

            if not evento or len(evento) > 255:
                errores['evento'] = 'El evento es obligatorio y debe tener menos de 255 caracteres.'

            if errores:
                return JsonResponse({'errores': errores}, status=400)

            # Crear el registro de kilometraje
            Kilometraje.objects.create(
                id_vehiculo=vehiculo,
                fecha_registro=fecha_registro,
                kilometraje=int(kilometraje),
                evento=evento
            )

            return JsonResponse({'mensaje': 'Kilometraje registrado exitosamente'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class UltimoKilometrajeView(View):
    def get(self, request, id_usuario, id_vehiculo, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token
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

            # Validar que el vehículo existe
            try:
                vehiculo = Vehiculo.objects.get(id_vehiculo=id_vehiculo)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Vehículo no encontrado'}, status=404)

            # Obtener el último kilometraje registrado
            kilometraje = Kilometraje.objects.filter(id_vehiculo=vehiculo).order_by('-fecha_registro').first()

            if not kilometraje:
                # Si no hay kilometraje, pero queremos mostrar la placa y marca
                return JsonResponse({
                    'error': 'No se ha registrado kilometraje para este vehículo',
                    'placa': vehiculo.placa,
                    'marca': vehiculo.marca,
                }, status=404)

            # Retornar el último kilometraje si se encuentra
            return JsonResponse({
                'id_vehiculo': vehiculo.id_vehiculo,
                'placa': vehiculo.placa,
                'marca': vehiculo.marca,
                'ultimo_kilometraje': kilometraje.kilometraje,
                'fecha_registro': kilometraje.fecha_registro,
                'evento': kilometraje.evento
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class TodosKilometrajesView(View):
    def get(self, request, id_usuario, id_vehiculo, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token
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

            # Validar que el vehículo existe
            try:
                vehiculo = Vehiculo.objects.get(id_vehiculo=id_vehiculo)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Vehículo no encontrado'}, status=404)

            # Obtener todos los kilometrajes registrados para el vehículo
            kilometrajes = Kilometraje.objects.filter(id_vehiculo=vehiculo).order_by('fecha_registro')

            if not kilometrajes:
                # Si no hay registros de kilometraje
                return JsonResponse({
                    'error': 'No se ha registrado kilometraje para este vehículo',
                    'placa': vehiculo.placa,
                    'marca': vehiculo.marca,
                }, status=404)

            # Construir la respuesta con todos los kilometrajes
            kilometrajes_data = []
            for kilometraje in kilometrajes:
                kilometrajes_data.append({
                    'id_vehiculo': vehiculo.id_vehiculo,
                    'placa': vehiculo.placa,
                    'marca': vehiculo.marca,
                    'kilometraje': kilometraje.kilometraje,
                    'fecha_registro': kilometraje.fecha_registro,
                    'evento': kilometraje.evento
                })

            # Retornar todos los kilometrajes
            return JsonResponse(kilometrajes_data, safe=False, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
