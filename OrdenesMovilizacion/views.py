from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import jwt
from datetime import datetime
from .models import OrdenesMovilizacion
from Vehiculos.models import Vehiculo
from Empleados.models import Empleados, Usuarios, Rol
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class CrearOrdenMovilizacionView(View):
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            # Validación de permisos y coincidencia de ID de usuario en la URL
            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=id_usuario)
            if usuario.id_rol.rol != 'Empleado':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtención de datos del formulario form-data
            secuencial_orden_movilizacion = request.POST.get('secuencial_orden_movilizacion')
            motivo_movilizacion = request.POST.get('motivo_movilizacion')
            lugar_origen_destino_movilizacion = request.POST.get('lugar_origen_destino_movilizacion')
            duracion_movilizacion = request.POST.get('duracion_movilizacion')
            id_conductor_id = request.POST.get('id_conductor')
            id_vehiculo_id = request.POST.get('id_vehiculo')
            fecha_viaje = request.POST.get('fecha_viaje')
            hora_ida = request.POST.get('hora_ida')
            hora_regreso = request.POST.get('hora_regreso')
            estado_movilizacion = request.POST.get('estado_movilizacion')

            # Obtención de objetos relacionados por ID
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)
            id_conductor = Empleados.objects.get(id_empleado=id_conductor_id)
            id_vehiculo = Vehiculo.objects.get(id_vehiculo=id_vehiculo_id)

            # Creación de la orden de movilización
            orden = OrdenesMovilizacion.objects.create(
                secuencial_orden_movilizacion=secuencial_orden_movilizacion,
                fecha_hora_emision=datetime.now(),
                fecha_viaje=fecha_viaje,
                hora_ida=hora_ida,
                hora_regreso=hora_regreso,
                estado_movilizacion=estado_movilizacion,
                id_empleado=empleado,
                motivo_movilizacion=motivo_movilizacion,
                lugar_origen_destino_movilizacion=lugar_origen_destino_movilizacion,
                duracion_movilizacion=duracion_movilizacion,
                id_conductor=id_conductor,
                id_vehiculo=id_vehiculo,
                habilitado=1
            )

            return JsonResponse({'message': 'Solicitud creada correctamente', 'id_orden_movilizacion': orden.id_orden_movilizacion})

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)

        except Vehiculo.DoesNotExist:
            return JsonResponse({"error": "Vehículo no encontrado"}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListarOrdenMovilizacionView(View):
    def get(self, request, id_usuario):
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

            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)
            ordenes = OrdenesMovilizacion.objects.filter(id_empleado=empleado)

            lista_ordenes = []
            for orden in ordenes:
                lista_ordenes.append({
                    'id_orden_movilizacion': orden.id_orden_movilizacion,
                    'secuencial_orden_movilizacion': orden.secuencial_orden_movilizacion,
                    'fecha_hora_emision': orden.fecha_hora_emision.strftime('%Y-%m-%d %H:%M:%S'),
                    'motivo_movilizacion': orden.motivo_movilizacion,
                    'lugar_origen_destino_movilizacion': orden.lugar_origen_destino_movilizacion,
                    'duracion_movilizacion': str(orden.duracion_movilizacion),
                    'id_conductor': orden.id_conductor.id_empleado,
                    'id_vehiculo': orden.id_vehiculo.id_vehiculo,
                    'fecha_viaje': orden.fecha_viaje.strftime('%Y-%m-%d'),
                    'hora_ida': orden.hora_ida.strftime('%H:%M:%S'),
                    'hora_regreso': orden.hora_regreso.strftime('%H:%M:%S'),
                    'estado_movilizacion': orden.estado_movilizacion,
                    'id_empleado': orden.id_empleado.id_empleado,
                    'habilitado': orden.habilitado,
                })

            return JsonResponse(lista_ordenes, safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)
        
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)
        
        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
        
        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        



@method_decorator(csrf_exempt, name='dispatch')
class EditarOrdenMovilizacionView(View):
    def put(self, request, id_usuario, id_orden):
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

            # Obtén la orden a editar
            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)

            # Verifica que el usuario tenga permiso para editar esta orden
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)
            if orden.id_empleado != empleado:
                return JsonResponse({'error': 'No tienes permisos suficientes para editar esta orden'}, status=403)

            # Actualiza los campos de la orden con los datos del formulario form-data
            orden.secuencial_orden_movilizacion = request.POST.get('secuencial_orden_movilizacion', orden.secuencial_orden_movilizacion)
            orden.motivo_movilizacion = request.POST.get('motivo_movilizacion', orden.motivo_movilizacion)
            orden.lugar_origen_destino_movilizacion = request.POST.get('lugar_origen_destino_movilizacion', orden.lugar_origen_destino_movilizacion)
            orden.duracion_movilizacion = request.POST.get('duracion_movilizacion', orden.duracion_movilizacion)
            orden.fecha_viaje = request.POST.get('fecha_viaje', orden.fecha_viaje)
            orden.hora_ida = request.POST.get('hora_ida', orden.hora_ida)
            orden.hora_regreso = request.POST.get('hora_regreso', orden.hora_regreso)
            orden.estado_movilizacion = request.POST.get('estado_movilizacion', orden.estado_movilizacion)
            orden.id_conductor_id = request.POST.get('id_conductor', orden.id_conductor.id_empleado)
            orden.id_vehiculo_id = request.POST.get('id_vehiculo', orden.id_vehiculo.id_vehiculo)
            orden.save()

            return JsonResponse({'mensaje': 'Orden de movilización editada correctamente'})

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)

        except Vehiculo.DoesNotExist:
            return JsonResponse({"error": "Vehículo no encontrado"}, status=404)

        except OrdenesMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CancelarOrdenMovilizacionView(View):
    def put(self, request, id_orden):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)
            orden.estado_movilizacion = 'Cancelado'
            orden.habilitado = 0
            orden.save()

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'mensaje': 'Orden de movilización cancelada exitosamente'
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)
        
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)
        
        except OrdenesMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
   
        
@method_decorator(csrf_exempt, name='dispatch')
class DetalleOrdenMovilizacion(View):
    def get(self, request, id_usuario, id_orden):
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

            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)
            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden, id_empleado=empleado)

            detalle_orden = {
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'secuencial_orden_movilizacion': orden.secuencial_orden_movilizacion,
                'fecha_hora_emision': orden.fecha_hora_emision.strftime('%Y-%m-%d %H:%M:%S'),
                'motivo_movilizacion': orden.motivo_movilizacion,
                'lugar_origen_destino_movilizacion': orden.lugar_origen_destino_movilizacion,
                'duracion_movilizacion': str(orden.duracion_movilizacion),
                'id_conductor': orden.id_conductor.id_empleado,
                'id_vehiculo': orden.id_vehiculo.id_vehiculo,
                'fecha_viaje': orden.fecha_viaje.strftime('%Y-%m-%d'),
                'hora_ida': orden.hora_ida.strftime('%H:%M:%S'),
                'hora_regreso': orden.hora_regreso.strftime('%H:%M:%S'),
                'estado_movilizacion': orden.estado_movilizacion,
                'id_empleado': orden.id_empleado.id_empleado,
                'habilitado': orden.habilitado,
            }

            return JsonResponse(detalle_orden)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)

        except OrdenesMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
