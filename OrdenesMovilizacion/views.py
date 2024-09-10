from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
import jwt
from .models import *
from datetime import datetime
from Vehiculos.models import Vehiculo
from Empleados.models import Empleados, Usuarios
from rest_framework.exceptions import AuthenticationFailed
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from weasyprint import HTML, CSS

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
            hora_ida_str = request.POST.get('hora_ida')
            hora_regreso_str = request.POST.get('hora_regreso')
            estado_movilizacion = request.POST.get('estado_movilizacion')

            if len(motivo_movilizacion) > 30:
                return JsonResponse({'error': 'El motivo de movilización no puede exceder los 30 caracteres'}, status=400)

            # Convertir strings de hora a objetos datetime.time
            hora_ida = datetime.strptime(hora_ida_str, '%H:%M').time()
            hora_regreso = datetime.strptime(hora_regreso_str, '%H:%M').time()

            # Validación de horas y duraciones con el modelo HorarioOrdenMovilizacion
            horario = HorarioOrdenMovilizacion.objects.first()  # Obtener los límites de horario
            if not horario.hora_ida_minima <= hora_ida <= horario.hora_llegada_maxima:
                return JsonResponse({'error': 'La hora de ida o regreso no está dentro del rango permitido'}, status=400)

            duracion_calculada = (datetime.combine(datetime.today(), hora_regreso) - datetime.combine(datetime.today(), hora_ida)).total_seconds() / 60
            if not horario.duracion_minima <= duracion_calculada <= horario.duracion_maxima:
                return JsonResponse({'error': 'La duración no está dentro del rango permitido'}, status=400)

            # Validación de la ruta
            ruta = RutasMovilizacion.objects.filter(ruta_descripcion=lugar_origen_destino_movilizacion, ruta_estado=1).first()
            if not ruta:
                return JsonResponse({'error': 'La ruta no coincide con ninguna ruta activa registrada'}, status=400)

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
    def post(self, request, id_usuario, id_orden):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)

            if payload.get('id_usuario') != id_usuario:
                return JsonResponse({'error': 'No tienes permiso para editar esta orden'}, status=403)

            orden.motivo_movilizacion = request.POST.get('motivo_movilizacion', orden.motivo_movilizacion)
            orden.duracion_movilizacion = request.POST.get('duracion_movilizacion', orden.duracion_movilizacion)
            id_conductor_id = request.POST.get('id_conductor', orden.id_conductor.id_empleado if orden.id_conductor else '')
            id_vehiculo_id = request.POST.get('id_vehiculo', orden.id_vehiculo.id_vehiculo if orden.id_vehiculo else '')
            orden.fecha_viaje = request.POST.get('fecha_viaje', orden.fecha_viaje)

            if len(orden.motivo_movilizacion) > 30:
                return JsonResponse({'error': 'El motivo de movilización no puede exceder los 30 caracteres'}, status=400)

            hora_ida_str = request.POST.get('hora_ida', orden.hora_ida)
            hora_regreso_str = request.POST.get('hora_regreso', orden.hora_regreso)

            if hora_ida_str and hora_regreso_str:
                # Ajustar el formato de hora para manejar 'HH:MM' o 'HH:MM:SS'
                try:
                    hora_ida = datetime.strptime(hora_ida_str, '%H:%M').time()
                except ValueError:
                    hora_ida = datetime.strptime(hora_ida_str, '%H:%M:%S').time()
                
                try:
                    hora_regreso = datetime.strptime(hora_regreso_str, '%H:%M').time()
                except ValueError:
                    hora_regreso = datetime.strptime(hora_regreso_str, '%H:%M:%S').time()

                horario = HorarioOrdenMovilizacion.objects.first()
                if not horario.hora_ida_minima <= hora_ida <= horario.hora_llegada_maxima:
                    return JsonResponse({'error': 'La hora de ida o regreso no está dentro del rango permitido'}, status=400)

                duracion_calculada = (datetime.combine(datetime.today(), hora_regreso) - datetime.combine(datetime.today(), hora_ida)).total_seconds() / 60
                if not horario.duracion_minima <= duracion_calculada <= horario.duracion_maxima:
                    return JsonResponse({'error': 'La duración no está dentro del rango permitido'}, status=400)

            ruta = RutasMovilizacion.objects.filter(ruta_descripcion=orden.lugar_origen_destino_movilizacion, ruta_estado=1).first()
            if not ruta:
                return JsonResponse({'error': 'La ruta no coincide con ninguna ruta activa registrada'}, status=400)

            id_conductor = Empleados.objects.get(id_empleado=id_conductor_id)
            id_vehiculo = Vehiculo.objects.get(id_vehiculo=id_vehiculo_id)

            orden.id_conductor = id_conductor
            orden.id_vehiculo = id_vehiculo

            orden.save()

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'mensaje': 'Orden de movilización actualizada exitosamente'
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except OrdenesMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)

        except Vehiculo.DoesNotExist:
            return JsonResponse({"error": "Vehículo no encontrado"}, status=404)

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
            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)

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
        
@method_decorator(csrf_exempt, name='dispatch')
class CancelarOrdenMovilizacionView(View):
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

            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden, id_empleado__id_persona=usuario.id_persona)

            if orden.estado_movilizacion == 'Cancelado':
                return JsonResponse({'error': 'La orden ya está cancelada'}, status=400)

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
class HabilitarOrdenMovilizacionView(View):
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

            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden, id_empleado__id_persona=usuario.id_persona)

            if orden.habilitado == 1:
                return JsonResponse({'error': 'La orden ya está habilitada'}, status=400)

            orden.estado_movilizacion = 'Pendiente'
            orden.habilitado = 1
            orden.save()

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'mensaje': 'Orden de movilización habilitada exitosamente'
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
class ListarTodasOrdenMovilizacionView(View):
    def get(self, request, id_usuario):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            if usuario.id_rol.rol != 'Administrador':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            ordenes = OrdenesMovilizacion.objects.all()

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

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RechazarOrdenMovilizacionView(View):
    def post(self, request, id_usuario, id_orden):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=id_usuario)
            if usuario.id_rol.rol != 'Administrador':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)

            if orden.estado_movilizacion == 'Denegado':
                return JsonResponse({'error': 'La orden ya está denegada'}, status=400)
            
            if orden.estado_movilizacion == 'Aprobado':
                return JsonResponse({'error': 'La orden ya está aprobada'}, status=400)
            
            if orden.habilitado == 0:
                return JsonResponse({'error': 'La Orden está cancelada'})

            motivo = request.POST.get('motivo')
            if not motivo:
                return JsonResponse({'error': 'El motivo es obligatorio'}, status=400)
            motivo_formateado = f'Denegado: {motivo}'

            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            with transaction.atomic():
                orden.estado_movilizacion = 'Denegado'
                orden.save()

                MotivoOrdenMovilizacion.objects.create(
                    id_orden_movilizacion=orden,
                    id_empleado=empleado,  
                    motivo=motivo_formateado
                )

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'mensaje': 'Orden de movilización denegada exitosamente'
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except OrdenesMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AprobarOrdenMovilizacionView(View):
    def post(self, request, id_usuario, id_orden):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=id_usuario)
            if usuario.id_rol.rol != 'Administrador':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)

            if orden.estado_movilizacion == 'Aprobado':
                return JsonResponse({'error': 'La orden ya está aprobada'}, status=400)

            if orden.estado_movilizacion == 'Denegado':
                return JsonResponse({'error': 'La orden ya está denegada'}, status=400)
            
            if orden.habilitado == 0:
                return JsonResponse({'error': 'La Orden está cancelada'})
            
            secuencial_orden_movilizacion = request.POST.get('secuencial_orden_movilizacion')
            if not secuencial_orden_movilizacion:
                return JsonResponse({'error': 'El campo Secuencial es obligatorio'}, status=400)
            
            if OrdenesMovilizacion.objects.filter(secuencial_orden_movilizacion=secuencial_orden_movilizacion).exists():
                return JsonResponse({'error': 'El secuencial ya está asignado a otra orden'}, status=400)

            orden.secuencial_orden_movilizacion = secuencial_orden_movilizacion

            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            motivo = request.POST.get('motivo', '')
            if motivo:
                motivo_formateado = f'Aprobado: {motivo}'
            else:
                motivo_formateado = 'Aprobado'


            with transaction.atomic():
                orden.estado_movilizacion = 'Aprobado'
                orden.save()

                MotivoOrdenMovilizacion.objects.create(
                    id_orden_movilizacion=orden,
                    id_empleado=empleado,  
                    motivo=motivo_formateado
                )

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'mensaje': 'Orden de movilización aprobada exitosamente'
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except OrdenesMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListarMotivoOrdenesMovilizacionView(View):
    def get(self, request, id_usuario):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            motivos = MotivoOrdenMovilizacion.objects.all()

            lista_motivos = []
            for motivo in motivos:
                lista_motivos.append({
                    'id_motivo_orden': motivo.id_motivo_orden,
                    'id_empleado': motivo.id_empleado.id_empleado,
                    'id_orden_movilizacion': motivo.id_orden_movilizacion.id_orden_movilizacion,
                    'motivo': motivo.motivo,
                    'fecha': motivo.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                })

            return JsonResponse(lista_motivos, safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarMotivoOrdenMovilizacionView(View):
    def post(self, request, id_usuario, id_orden, id_motivo):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'No tienes permiso para editar esta orden'}, status=403)

            # Verificar y obtener la orden
            try:
                orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)
            except OrdenesMovilizacion.DoesNotExist:
                return JsonResponse({'error': 'Orden no encontrada'}, status=404)

            # Verificar y obtener el motivo
            try:
                motivo = MotivoOrdenMovilizacion.objects.get(id_motivo_orden=id_motivo, id_orden_movilizacion=orden)
            except MotivoOrdenMovilizacion.DoesNotExist:
                return JsonResponse({'error': 'Motivo no encontrado'}, status=404)

            nuevo_estado = request.POST.get('estado')
            nuevo_motivo = request.POST.get('motivo')
            nuevo_secuencial = request.POST.get('secuencial')

            if nuevo_estado:
                if nuevo_estado == 'Aprobado':
                    # Actualizar solo si el estado cambia de 'Denegado' a 'Aprobado'
                    if orden.estado_movilizacion == 'Denegado':
                        orden.estado_movilizacion = 'Aprobado'
                    # Siempre actualizar el secuencial si es 'Aprobado'
                    orden.secuencial_orden_movilizacion = nuevo_secuencial or '0000'
                elif nuevo_estado == 'Denegado':
                    orden.estado_movilizacion = 'Denegado'
                    orden.secuencial_orden_movilizacion = '0000'
                else:
                    # Otros estados
                    orden.estado_movilizacion = nuevo_estado
                    if nuevo_secuencial:
                        orden.secuencial_orden_movilizacion = nuevo_secuencial

            # Actualizar el motivo en la tabla de motivos
            if nuevo_motivo:
                motivo.motivo = nuevo_motivo
                motivo.save()

            orden.save()

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'mensaje': 'Orden de movilización actualizada exitosamente'
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def generar_pdf(orden):
    try:
        template_path = 'ordenes_movilizacion_pdf.html'

        conductor_persona = orden.id_conductor.id_persona
        empleado_persona = orden.id_empleado.id_persona

        # Convertir la duración al formato "00:30hrs"
        duracion = orden.duracion_movilizacion
        horas = duracion.hour
        minutos = duracion.minute
        duracion_formateada = f"{horas:02}:{minutos:02}hrs"

        fecha_actual = datetime.now().strftime('%d/%m/%Y')

        context = {
            'orden': orden,
            'secuencial': orden.secuencial_orden_movilizacion,
            'conductor': orden.id_conductor,
            'conductor_persona': conductor_persona,
            'vehiculo': orden.id_vehiculo,
            'empleado': orden.id_empleado,
            'empleado_persona': empleado_persona,
            'duracion_formateada': duracion_formateada,
            'fecha_actual': fecha_actual,  
        }

        html = render_to_string(template_path, context)

        pdf_file = BytesIO()
        HTML(string=html).write_pdf(pdf_file)

        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="orden_{orden.id_orden_movilizacion}.pdf"'
        return response

    except Exception as e:
        logger.error(f'Error en generar_pdf: {str(e)}')
        return HttpResponse(f'Error al generar el PDF: {str(e)}', status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GenerarPdfOrdenMovilizacionView(View):
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

            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)
            if not orden:
                return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)


            return generar_pdf(orden)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except OrdenesMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)

        except Exception as e:
            print(f'Error al generar el PDF: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListarOrdenesAprobadasView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            # Filtra las órdenes de movilización con estado "Aprobado"
            ordenes_aprobadas = OrdenesMovilizacion.objects.filter(estado_movilizacion='Aprobado').values(
                'id_orden_movilizacion', 'secuencial_orden_movilizacion', 'fecha_hora_emision',
                'motivo_movilizacion', 'lugar_origen_destino_movilizacion', 'duracion_movilizacion',
                'id_conductor', 'id_vehiculo', 'fecha_viaje', 'hora_ida', 'hora_regreso', 'estado_movilizacion',
                'id_empleado', 'habilitado'
            )
            ordenes_aprobadas_list = list(ordenes_aprobadas)

            return JsonResponse({'ordenes_aprobadas': ordenes_aprobadas_list}, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class EditarHorarioView(View):
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            data = request.POST
            hora_ida_minima = data.get('hora_ida_minima')
            hora_llegada_maxima = data.get('hora_llegada_maxima')
            duracion_minima = data.get('duracion_minima')
            duracion_maxima = data.get('duracion_maxima')

            if not hora_ida_minima or not hora_llegada_maxima or not duracion_minima or not duracion_maxima:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            with transaction.atomic():
                try:
                    horario = HorarioOrdenMovilizacion.objects.get()
                    horario.hora_ida_minima = hora_ida_minima
                    horario.hora_llegada_maxima = hora_llegada_maxima
                    horario.duracion_minima = int(duracion_minima)
                    horario.duracion_maxima = int(duracion_maxima)
                    horario.save()
                    message = 'Horario actualizado exitosamente'
                except HorarioOrdenMovilizacion.DoesNotExist:
                    horario = HorarioOrdenMovilizacion(
                        hora_ida_minima=hora_ida_minima,
                        hora_llegada_maxima=hora_llegada_maxima,
                        duracion_minima=int(duracion_minima),
                        duracion_maxima=int(duracion_maxima) 
                    )
                    horario.save()
                    message = 'Horario creado exitosamente'

            return JsonResponse({'message': message}, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class VerHorarioView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            horario = HorarioOrdenMovilizacion.objects.first()

            if not horario:
                return JsonResponse({'horario': {}}, status=200)  

            horario_data = {
                'hora_ida_minima': horario.hora_ida_minima,
                'hora_llegada_maxima': horario.hora_llegada_maxima,
                'duracion_minima': horario.duracion_minima,
                'duracion_maxima': horario.duracion_maxima,
            }

            return JsonResponse({'horario': horario_data}, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CrearRutaView(View):
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            data = request.POST
            ruta_origen = data.get('ruta_origen')
            ruta_destino = data.get('ruta_destino')
            ruta_descripcion = data.get('ruta_descripcion')
            ruta_estado = data.get('ruta_estado')

            if not ruta_origen or not ruta_destino or not ruta_descripcion or not ruta_estado:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            RutasMovilizacion.objects.create(
                ruta_origen=ruta_origen,
                ruta_destino=ruta_destino,
                ruta_descripcion=ruta_descripcion,
                ruta_estado=ruta_estado
            )
            
            return JsonResponse({'message': 'Ruta creada exitosamente'}, status=201)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarRutaView(View):
    def post(self, request, id_usuario, id_ruta_movilizacion, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            data = request.POST
            ruta_origen = data.get('ruta_origen')
            ruta_destino = data.get('ruta_destino')
            ruta_descripcion = data.get('ruta_descripcion')
            ruta_estado = data.get('ruta_estado')

            if not ruta_origen or not ruta_destino or not ruta_descripcion or not ruta_estado:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            try:
                ruta = RutasMovilizacion.objects.get(id_ruta_movilizacion=id_ruta_movilizacion)
                ruta.ruta_origen=ruta_origen
                ruta.ruta_destino=ruta_destino
                ruta.ruta_descripcion = ruta_descripcion
                ruta.ruta_estado = ruta_estado
                ruta.save()
                return JsonResponse({'message': 'Ruta actualizada exitosamente'}, status=200)
            except RutasMovilizacion.DoesNotExist:
                return JsonResponse({'error': 'Ruta no encontrada'}, status=404)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListarRutasView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            rutas = RutasMovilizacion.objects.all().values('id_ruta_movilizacion', 'ruta_origen', 'ruta_destino', 'ruta_descripcion', 'ruta_estado')
            rutas_list = list(rutas)

            return JsonResponse({'rutas': rutas_list}, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)