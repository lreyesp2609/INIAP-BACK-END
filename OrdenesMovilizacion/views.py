from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
import jwt
from .models import OrdenesMovilizacion, MotivoOrdenMovilizacion
from datetime import datetime
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
    def post(self, request, id_usuario, id_orden):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            orden = OrdenesMovilizacion.objects.get(id_orden_movilizacion=id_orden)

            # Verificar que el usuario tenga permiso para editar esta orden
            if payload.get('id_usuario') != id_usuario:
                return JsonResponse({'error': 'No tienes permiso para editar esta orden'}, status=403)

            # Obtener datos del formulario
            orden.motivo_movilizacion = request.POST.get('motivo_movilizacion', orden.motivo_movilizacion)
            orden.duracion_movilizacion = request.POST.get('duracion_movilizacion', orden.duracion_movilizacion)
            id_conductor_id = request.POST.get('id_conductor', orden.id_conductor.id_empleado if orden.id_conductor else '')
            id_vehiculo_id = request.POST.get('id_vehiculo', orden.id_vehiculo.id_vehiculo if orden.id_vehiculo else '')
            orden.fecha_viaje = request.POST.get('fecha_viaje', orden.fecha_viaje)
            orden.hora_ida = request.POST.get('hora_ida', orden.hora_ida)
            orden.hora_regreso = request.POST.get('hora_regreso', orden.hora_regreso)

            # Buscar objetos relacionados por ID
            id_conductor = Empleados.objects.get(id_empleado=id_conductor_id)
            id_vehiculo = Vehiculo.objects.get(id_vehiculo=id_vehiculo_id)

            # Asignar nuevos valores
            orden.id_conductor = id_conductor
            orden.id_vehiculo = id_vehiculo

            # Guardar la orden actualizada
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

            motivo = request.POST.get('motivo', 'Aprobado')
            motivo_formateado = f'Aprobado: {motivo}'

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

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=id_usuario)
            if usuario.id_rol.rol != 'Administrador':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

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
    def post(self, request, id_usuario, id_motivo):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            motivo_orden = MotivoOrdenMovilizacion.objects.get(id_motivo_orden=id_motivo)

            # Verificar que el usuario tenga permiso para editar este motivo
            if motivo_orden.id_empleado.id_persona.id_usuario != id_usuario:
                return JsonResponse({'error': 'No tienes permiso para editar este motivo'}, status=403)

            # Obtener datos del formulario
            motivo_orden.motivo = request.POST.get('motivo', motivo_orden.motivo)

            # Guardar el motivo actualizado
            motivo_orden.save()

            return JsonResponse({
                'id_motivo_orden': motivo_orden.id_motivo_orden,
                'mensaje': 'Motivo de orden de movilización actualizado exitosamente'
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except MotivoOrdenMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Motivo de orden de movilización no encontrado"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EditarSecuencialOrdenMovilizacionView(View):
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

            # Obtener datos del formulario
            orden.secuencial_orden_movilizacion = request.POST.get('secuencial_orden_movilizacion', orden.secuencial_orden_movilizacion)

            # Guardar la orden actualizada
            orden.save()

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'mensaje': 'Secuencial de orden de movilización actualizado exitosamente'
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except OrdenesMovilizacion.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
