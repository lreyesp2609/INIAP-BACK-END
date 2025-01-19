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
            kilometraje_obj = Kilometraje.objects.create(
                id_vehiculo=vehiculo,
                fecha_registro=fecha_registro,
                kilometraje=int(kilometraje),
                evento=evento
            )

            # Llamar a la comparación de kilometraje
            CompararKilometrajeView().post(request, id_vehiculo=id_vehiculo)

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
        
@method_decorator(csrf_exempt, name='dispatch')
class GestionarAlertasMantenimientoView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_vehiculo, *args, **kwargs):
        try:
            # Validar el token de autenticación
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
            kilometraje_activacion = request.POST.get('kilometraje_activacion')
            tipo_mantenimiento = request.POST.get('tipo_mantenimiento')

            # Validaciones de los datos
            errores = {}
            if not kilometraje_activacion or not kilometraje_activacion.isdigit() or int(kilometraje_activacion) < 0:
                errores['kilometraje_activacion'] = 'El kilometraje debe ser un número entero positivo.'

            if not tipo_mantenimiento or len(tipo_mantenimiento) > 255:
                errores['tipo_mantenimiento'] = 'El tipo de mantenimiento es obligatorio y debe tener menos de 255 caracteres.'

            if errores:
                return JsonResponse({'errores': errores}, status=400)

            # Buscar si ya existe una alerta para este vehículo y tipo de mantenimiento
            alerta, creada = AlertasMantenimiento.objects.update_or_create(
                id_vehiculo=vehiculo,
                tipo_mantenimiento=tipo_mantenimiento,
                defaults={
                    'kilometraje_activacion': int(kilometraje_activacion),
                    'estado_alerta': True  # Activar la alerta al crear o actualizar
                }
            )

            # Llamar a la comparación de kilometraje
            CompararKilometrajeView().post(request, id_vehiculo=id_vehiculo)

            if creada:
                mensaje = 'Alerta de mantenimiento creada exitosamente.'
            else:
                mensaje = 'Alerta de mantenimiento actualizada exitosamente.'

            return JsonResponse({'mensaje': mensaje}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CompararKilometrajeView(View):
    @transaction.atomic
    def post(self, request, id_vehiculo, *args, **kwargs):
        try:
            # Validar el token de autenticación
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

            # Validar que el vehículo existe
            try:
                vehiculo = Vehiculo.objects.get(id_vehiculo=id_vehiculo)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Vehículo no encontrado'}, status=404)

            # Obtener el último registro de kilometraje para el vehículo
            kilometraje = Kilometraje.objects.filter(id_vehiculo=vehiculo).order_by('-fecha_registro').first()
            if not kilometraje:
                return JsonResponse({'error': 'No se ha registrado kilometraje para este vehículo'}, status=404)

            # Obtener todas las alertas asociadas al vehículo
            alertas = AlertasMantenimiento.objects.filter(id_vehiculo=vehiculo)

            if not alertas:
                return JsonResponse({'mensaje': 'No hay alertas de mantenimiento para este vehículo'}, status=200)

            # Actualizar el estado de las alertas según el kilometraje actual
            alertas_actualizadas = []
            for alerta in alertas:
                if kilometraje.kilometraje >= alerta.kilometraje_activacion:
                    alerta.estado_alerta = True
                else:
                    alerta.estado_alerta = False
                alerta.save()
                alertas_actualizadas.append({
                    'id_alerta': alerta.id_alerta,
                    'kilometraje_activacion': alerta.kilometraje_activacion,
                    'estado_alerta': alerta.estado_alerta
                })

            return JsonResponse({
                'mensaje': 'Estado de alertas actualizado',
                'alertas_actualizadas': alertas_actualizadas
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ListarAlertasActivasView(View):
    @method_decorator(csrf_exempt, name='dispatch')
    def get(self, request, *args, **kwargs):
        try:
            # Verificación del token
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

            # Obtener todas las alertas activas (estado_alerta == True)
            alertas_activas = AlertasMantenimiento.objects.filter(estado_alerta=True)

            if not alertas_activas:
                return JsonResponse({'error': 'No hay alertas activas'}, status=404)

            # Crear la lista de resultados con la información requerida
            alertas_data = []
            for alerta in alertas_activas:
                vehiculo = alerta.id_vehiculo

                alertas_data.append({
                    'placa': vehiculo.placa,
                    'modelo': vehiculo.modelo,
                    'kilometraje': alerta.kilometraje_activacion,
                    'tipo_mantenimiento': alerta.tipo_mantenimiento
                })

            return JsonResponse(alertas_data, safe=False, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
