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
from Empleados.models import *
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

            # Obtener empleado relacionado al usuario
            try:
                empleado = Empleados.objects.get(id_persona=token_id_usuario)  # Ajusta según tu estructura real
            except Empleados.DoesNotExist:
                return JsonResponse({'error': 'Empleado no encontrado'}, status=404)

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
                empleado=empleado,  # Añadido el empleado
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
            kilometrajes = Kilometraje.objects.filter(
                id_vehiculo=vehiculo
            ).select_related(
                'empleado__id_persona'  # Incluir la relación con Personas
            ).order_by('fecha_registro')

            if not kilometrajes:
                return JsonResponse({
                    'error': 'No se ha registrado kilometraje para este vehículo',
                    'placa': vehiculo.placa,
                    'marca': vehiculo.marca,
                }, status=404)

            kilometrajes_data = []
            for kilometraje in kilometrajes:
                # Acceder a los datos de persona a través de empleado
                persona = kilometraje.empleado.id_persona
                
                kilometrajes_data.append({
                    'id_vehiculo': vehiculo.id_vehiculo,
                    'placa': vehiculo.placa,
                    'marca': vehiculo.marca,
                    'kilometraje': kilometraje.kilometraje,
                    'fecha_registro': kilometraje.fecha_registro,
                    'evento': kilometraje.evento,
                    'registrado_por': f"{persona.nombres} {persona.apellidos}"  # Nuevo campo
                })

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

class ListarDetalleAlertasView(View):
    def get(self, request, id_usuario, id_vehiculo, *args, **kwargs):
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

            # Obtener las alertas de mantenimiento para este vehículo
            alertas = AlertasMantenimiento.objects.filter(id_vehiculo=vehiculo)

            # Si no hay alertas de mantenimiento, responder con un mensaje
            if not alertas.exists():
                return JsonResponse({'mensaje': 'No se encontraron alertas de mantenimiento para este vehículo'}, status=404)

            # Construir la respuesta con los detalles de las alertas
            alertas_listado = []
            for alerta in alertas:
                alertas_listado.append({
                    'kilometraje_activacion': alerta.kilometraje_activacion,
                    'tipo_mantenimiento': alerta.tipo_mantenimiento,
                })

            # Devolver las alertas con detalles en formato JSON
            return JsonResponse({'alertas': alertas_listado}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        



from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from rest_framework.exceptions import AuthenticationFailed
from io import BytesIO
import jwt
from django.conf import settings
from weasyprint import HTML
from .models import Kilometraje  # Asegúrate de importar tu modelo
from datetime import datetime

@method_decorator(csrf_exempt, name='dispatch')
class GenerarReporteKilometrajeView(View):
    def post(self, request, id_usuario):
        try:
            # Autenticación con JWT (igual al ejemplo)
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)
            
            # Obtener parámetros de filtro
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            vehiculo = request.POST.get('vehiculo')
            empleado = request.POST.get('empleado')
            evento = request.POST.get('evento')

            # Validación de fechas
            if fecha_inicio and fecha_fin:
                try:
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                    if fecha_inicio_dt > fecha_fin_dt:
                        return JsonResponse({'error': 'La fecha de inicio no puede ser mayor que la fecha de fin'}, status=400)
                except ValueError:
                    return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

            # Construir filtros
            filtros = {}
            if fecha_inicio and fecha_fin:
                filtros['fecha_registro__range'] = [fecha_inicio, fecha_fin]
            if vehiculo:
                filtros['id_vehiculo'] = vehiculo
            if empleado:
                filtros['empleado'] = empleado
            if evento:
                filtros['evento__icontains'] = evento

            registros = Kilometraje.objects.filter(**filtros).select_related('id_vehiculo', 'empleado')
            
            # Preparar datos para el reporte
            lista_registros = []
            total_kilometros = 0
            
            for registro in registros:
                vehiculo = registro.id_vehiculo
                empleado_reg = registro.empleado.id_persona
                
                lista_registros.append({
                    'fecha_registro': registro.fecha_registro.strftime('%Y-%m-%d'),
                    'vehiculo_placa': vehiculo.placa,
                    'vehiculo_marca': vehiculo.marca,
                    'empleado_nombres': f"{empleado_reg.nombres} {empleado_reg.apellidos}",
                    'kilometraje': registro.kilometraje,
                    'evento': registro.evento,
                })
                total_kilometros += registro.kilometraje

            descripcion = self.generar_descripcion(filtros, registros, total_kilometros)
            
            # Determinar columnas a mostrar
            mostrar_vehiculo = 'id_vehiculo' not in filtros
            mostrar_empleado = 'empleado' not in filtros

            return self.generar_pdf(lista_registros, descripcion, mostrar_vehiculo, mostrar_empleado)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)
        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)
        except Exception as e:
            print(f'Error al generar el reporte: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

    def generar_descripcion(self, filtros, registros, total_kilometros):
        total_registros = registros.count()
        descripcion = "Resumen de registros de kilometraje: "

        if total_registros == 0:
            return "No se encontraron registros que cumplan con los filtros proporcionados."

        # Fechas
        if 'fecha_registro__range' in filtros:
            fecha_inicio, fecha_fin = filtros['fecha_registro__range']
            descripcion += f"entre las fechas <strong>{fecha_inicio}</strong> y <strong>{fecha_fin}</strong>, "

        # Vehículo
        if 'id_vehiculo' in filtros:
            vehiculo = registros.first().id_vehiculo
            descripcion += f"para el vehículo <strong>{vehiculo.placa} ({vehiculo.marca})</strong>, "

        # Empleado
        if 'empleado' in filtros:
            empleado = registros.first().empleado.id_persona
            descripcion += f"registrados por <strong>{empleado.nombres} {empleado.apellidos}</strong>, "

        # Evento
        if 'evento__icontains' in filtros:
            descripcion += f"con evento relacionado a <strong>{filtros['evento__icontains']}</strong>, "

        descripcion += f"se han registrado un total de <strong>{total_registros}</strong> eventos de kilometraje, "
        descripcion += f"sumando un total de <strong>{total_kilometros} km</strong>."

        return descripcion

    def generar_pdf(self, registros, descripcion, mostrar_vehiculo, mostrar_empleado):
        try:
            
            total_kilometros = sum(r['kilometraje'] for r in registros)

            context = {
                'registros': registros,
                'descripcion': descripcion,
                'mostrar_vehiculo': mostrar_vehiculo,
                'mostrar_empleado': mostrar_empleado,
                'total_kilometros': total_kilometros,
                'fecha_actual': datetime.now()
            }

            html_string = render_to_string('reporte_kilometraje.html', context)
            pdf_file = BytesIO()
            HTML(string=html_string).write_pdf(pdf_file)

            response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="reporte_kilometraje.pdf"'
            return response

        except Exception as e:
            return HttpResponse(f'Error al generar el PDF: {str(e)}', status=500)