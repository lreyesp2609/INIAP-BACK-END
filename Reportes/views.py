from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.exceptions import AuthenticationFailed
import xhtml2pdf.pisa as pisa
from io import BytesIO
import jwt
from django.conf import settings
from OrdenesMovilizacion.urls import OrdenesMovilizacion
from datetime import datetime


@method_decorator(csrf_exempt, name='dispatch')
class GenerarReporteOrdenesView(View):
    def post(self, request, id_usuario):
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
            
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            empleado = request.POST.get('empleado')
            conductor = request.POST.get('conductor')
            ruta = request.POST.get('ruta')
            vehiculo = request.POST.get('vehiculo')
            estado = int(request.POST.get('estado', 0)) 

            # Validación de fechas
            if fecha_inicio and fecha_fin:
                try:
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                    if fecha_inicio_dt > fecha_fin_dt:
                        return JsonResponse({'error': 'La fecha de inicio no puede ser mayor que la fecha de fin'}, status=400)
                except ValueError:
                    return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

            filtros = {}
            if fecha_inicio and fecha_fin:
                filtros['fecha_viaje__range'] = [fecha_inicio, fecha_fin]
            if empleado:
                filtros['id_empleado'] = empleado
            if conductor:
                filtros['id_conductor_id'] = conductor
            if vehiculo:
                filtros['id_vehiculo'] = vehiculo
            if ruta:
                filtros['lugar_origen_destino_movilizacion'] = ruta
            if estado == 1:
                filtros['estado_movilizacion'] = 'Aprobado'
            elif estado == 2:
                filtros['estado_movilizacion'] = 'Denegado'
            elif estado == 0:
                filtros['estado_movilizacion__in'] = ['Aprobado', 'Denegado']

            ordenes = OrdenesMovilizacion.objects.filter(**filtros)
            lista_ordenes = []
            for orden in ordenes:
                empleado = orden.id_empleado.id_persona
                conductor = orden.id_conductor.id_persona
                vehiculo = orden.id_vehiculo

                lista_ordenes.append({
                    'id_orden_movilizacion': orden.id_orden_movilizacion,
                    'secuencial_orden_movilizacion': orden.secuencial_orden_movilizacion,
                    'fecha_hora_emision': orden.fecha_hora_emision.strftime('%Y-%m-%d %H:%M:%S'),
                    'motivo_movilizacion': orden.motivo_movilizacion,
                    'lugar_origen_destino_movilizacion': orden.lugar_origen_destino_movilizacion,
                    'duracion_movilizacion': (orden.duracion_movilizacion.strftime('%H:%M')),
                    'conductor_nombres': f"{conductor.nombres}",
                    'conductor_apellidos': f"{conductor.apellidos}",
                    'vehiculo_placa': vehiculo.placa,
                    'fecha_viaje': orden.fecha_viaje.strftime('%Y-%m-%d'),
                    'hora_ida': orden.hora_ida.strftime('%H:%M'),
                    'hora_regreso': orden.hora_regreso.strftime('%H:%M'),
                    'estado_movilizacion': orden.estado_movilizacion,
                    'empleado_nombres': f"{empleado.nombres}",
                    'empleado_apellidos': f"{empleado.apellidos}",
                    'habilitado': orden.habilitado,
                })

            descripcion = generar_descripcion(filtros, ordenes)
            # Determinar qué columnas mostrar

            mostrar_estado =  estado in [1, 2]
            mostrar_funcionario = 'id_empleado' not in filtros
            mostrar_conductor = 'id_conductor_id' not in filtros
            mostrar_placa = 'id_vehiculo' not in filtros

            return generar_pdf(lista_ordenes, descripcion, mostrar_estado, mostrar_funcionario, mostrar_conductor, mostrar_placa)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            print(f'Error al generar el reporte: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
        

def generar_descripcion(filtros, ordenes):
    total_ordenes = ordenes.count()
    descripcion = "Resumen de solicitudes de movilización: "

    if total_ordenes == 0:
        return "No se encontraron solicitudes que cumplan con los filtros proporcionados."

    # Fechas
    if 'fecha_viaje__range' in filtros:
        fecha_inicio, fecha_fin = filtros['fecha_viaje__range']
        descripcion += f"entre las fechas <strong>{fecha_inicio}</strong> y <strong>{fecha_fin}</strong>, "

    # Funcionario
    if 'id_empleado' in filtros:
        empleado_obj = ordenes.first().id_empleado
        if empleado_obj:
            empleado_persona = empleado_obj.id_persona
            descripcion += f"para el funcionario <strong>{getattr(empleado_persona, 'apellidos', 'N/A')} {getattr(empleado_persona, 'nombres', 'N/A')}</strong>, "

    # Conductor
    if 'id_conductor_id' in filtros:
        conductor_obj = ordenes.first().id_conductor
        if conductor_obj:
            conductor_persona = conductor_obj.id_persona
            descripcion += f"con el conductor <strong>{getattr(conductor_persona, 'apellidos', 'N/A')} {getattr(conductor_persona, 'nombres', 'N/A')}</strong>, "

    # Vehículo
    if 'id_vehiculo' in filtros:
        vehiculo_obj = ordenes.first().id_vehiculo
        if vehiculo_obj:
            descripcion += f"utilizando el vehículo de placa <strong>{getattr(vehiculo_obj, 'placa', 'N/A')}</strong>, "

    # Ruta
    if 'lugar_origen_destino_movilizacion' in filtros:
        ruta = filtros['lugar_origen_destino_movilizacion']
        descripcion += f"para la ruta <strong>{ruta}</strong>, "

    # Conteo de aprobados y rechazados
    aprobados = ordenes.filter(estado_movilizacion='Aprobado').count()
    rechazados = ordenes.filter(estado_movilizacion='Denegado').count()

    if aprobados > 0 and rechazados > 0 and filtros.get('estado_movilizacion__in'):
        descripcion += f"se han registrado un total de <strong>{total_ordenes}</strong> solicitudes, de las cuales <strong>{aprobados}</strong> fueron aprobadas y <strong>{rechazados}</strong> fueron rechazadas."
    elif aprobados > 0 and rechazados == 0:
        descripcion += f"se han registrado un total de <strong>{aprobados}</strong> solicitudes aprobadas."
    elif rechazados > 0 and aprobados == 0:
        descripcion += f"se han registrado un total de <strong>{rechazados}</strong> solicitudes rechazadas."
    else:
        descripcion += f"se han registrado un total de <strong>{total_ordenes}</strong> solicitudes."

    return descripcion


def generar_pdf(ordenes, descripcion, mostrar_estado, mostrar_funcionario, mostrar_conductor, mostrar_placa):
    template_path = 'reporte_ordenes.html'
    context = {
        'ordenes': ordenes,
        'descripcion': descripcion,
        'mostrar_estado': mostrar_estado,
        'mostrar_funcionario': mostrar_funcionario,
        'mostrar_conductor': mostrar_conductor,
        'mostrar_placa': mostrar_placa
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_ordenes.pdf"'
    response['Content-Transfer-Encoding'] = 'binary'

    template = render_to_string(template_path, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), result)
    if not pdf.err:
        response.write(result.getvalue())
        return response
    else:
        return HttpResponse('Error al generar el PDF', status=500)
