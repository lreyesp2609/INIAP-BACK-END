from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.exceptions import AuthenticationFailed
from io import BytesIO
import jwt
from OrdenesMovilizacion.models import *
from Informes.models import *
from django.conf import settings
from datetime import datetime
from weasyprint import HTML
import locale
import pytz

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
            empleados = request.POST.getlist('empleados')  
            conductores = request.POST.getlist('conductores')  
            rutas = request.POST.getlist('rutas') 
            vehiculos = [int(v) for v in request.POST.getlist('vehiculos')]
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
            if empleados:
                filtros['id_empleado__in'] = empleados
            if conductores:
                filtros['id_conductor_id__in'] = conductores
            if vehiculos:
                filtros['id_vehiculo__in'] = vehiculos
            if rutas:
                filtros['lugar_origen_destino_movilizacion__in'] = rutas
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
            mostrar_estado =  estado in [1, 2]
            mostrar_funcionario = 'id_empleado' not in filtros
            mostrar_conductor = 'id_conductor_id' not in filtros
            mostrar_placa = 'id_vehiculo' not in filtros

            if ordenes.exists():
                return generar_pdf_ordenes(lista_ordenes, descripcion, mostrar_estado, mostrar_funcionario, mostrar_conductor, mostrar_placa)
            return generar_pdf_vacio("Ordenes de Movilización")

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            print(f'Error al generar el reporte: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class GenerarReporteInformeViajesView(View):
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

            # Filtrar por fechas, empleado y otros parámetros
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            empleado = request.POST.get('empleado')
            destino = request.POST.get('destino')
            tipo_transporte = request.POST.get('tipo_transporte')

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
                filtros['fecha_salida_informe__range'] = [fecha_inicio, fecha_fin]
            if empleado:
                filtros['id_solicitud__id_empleado'] = empleado
            if destino:
                filtros['id_solicitud__lugar_servicio'] = destino
            if tipo_transporte:
                filtros['transporteinformes__tipo_transporte_info'] = tipo_transporte

            informes = Informes.objects.filter(**filtros)
            lista_informes = []
            for informe in informes:
                solicitud = informe.id_solicitud
                empleado = solicitud.id_empleado.id_persona

                lista_informes.append({
                    'id_informe': informe.id_informes,
                    'codigo_solicitud': solicitud.generar_codigo_solicitud(),
                    'empleado_nombres': f"{empleado.nombres}",
                    'empleado_apellidos': f"{empleado.apellidos}",
                    'fecha_salida': informe.fecha_salida_informe.strftime('%Y-%m-%d') if informe.fecha_salida_informe else '',
                    'fecha_llegada': informe.fecha_llegada_informe.strftime('%Y-%m-%d') if informe.fecha_llegada_informe else '',
                    'lugar_servicio': solicitud.lugar_servicio,
                    'tipo_transporte': informe.transporteinformes.tipo_transporte_info if informe.transporteinformes else '',
                })

            # Generar el PDF con la lista de informes de viaje
            return generar_pdf_informe_viaje(lista_informes)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            print(f'Error al generar el reporte de informe de viajes: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GenerarReporteInformeFacturasView(View):
    def post(self, request, id_usuario):
        try:
            # Validación del token
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            # Obtener filtros
            empleados = request.POST.getlist('empleados')
            monto_min = request.POST.get('monto_min', None)
            monto_max = request.POST.get('monto_max', None)
            fecha_inicio = request.POST.get('fecha_inicio', None)
            fecha_fin = request.POST.get('fecha_fin', None)

            # Validación de fechas
            if fecha_inicio and fecha_fin:
                try:
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                    if fecha_inicio_dt > fecha_fin_dt:
                        return JsonResponse({'error': 'La fecha de inicio no puede ser mayor que la fecha de fin'}, status=400)
                except ValueError:
                    return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

            # Crear filtros
            filtros = {}
            if fecha_inicio and fecha_fin:
                filtros['fecha_emision__range'] = [fecha_inicio, fecha_fin]

            if empleados:
                empleados_ids = Empleados.objects.filter(
                    id_persona__nombres__in=empleados
                ).values_list('id_empleado', flat=True)
                filtros['id_informe__id_solicitud__id_empleado__id_empleado__in'] = empleados_ids

            if monto_min:
                filtros['valor__gte'] = float(monto_min)
            if monto_max:
                filtros['valor__lte'] = float(monto_max)

            # Filtrar las facturas
            facturas = FacturasInformes.objects.filter(**filtros).select_related(
                'id_informe__id_solicitud__id_empleado__id_persona'
            )

            # Generar PDF
            if facturas.exists():
                return generar_pdf_facturas(facturas)
            else:
                return generar_pdf_vacio("Reporte de Facturas")

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'El token ha expirado'}, status=401)
        except jwt.DecodeError:
            return JsonResponse({'error': 'Error al decodificar el token'}, status=401)
        except Exception as e:
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

def generar_pdf_ordenes(ordenes, descripcion, mostrar_estado, mostrar_funcionario, mostrar_conductor, mostrar_placa):
    try:
        context = {
            'ordenes': ordenes,
            'descripcion': descripcion,
            'mostrar_estado': mostrar_estado,
            'mostrar_funcionario': mostrar_funcionario,
            'mostrar_conductor': mostrar_conductor,
            'mostrar_placa': mostrar_placa
        }

        html_string = render_to_string('reporte_ordenes.html', context)

        pdf_file = BytesIO()
        HTML(string=html_string).write_pdf(pdf_file)

        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="reporte_ordenes.pdf"'
        response['Content-Transfer-Encoding'] = 'binary'
        
        return response

    except Exception as e:
        return HttpResponse(f'Error al generar el PDF: {str(e)}', status=500)
    
def generar_pdf_informe_viaje(informes):
    try:
        template_path = 'reporte_informe_viajes.html'  # Nombre del template
        current_date = datetime.now().strftime('%d-%m-%Y')
        
        context = {
            'informes': informes,
            'fecha_actual': current_date,
        }

        html_content = render_to_string(template_path, context)
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)

        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="reporte_informe_viajes.pdf"'

        return response

    except Exception as e:
        return HttpResponse(f'Error al generar el PDF: {str(e)}', status=500)

def generar_pdf_facturas(facturas):
    try:
        # Configuración de idioma y zona horaria
        current_date = datetime.now(pytz.timezone('America/Guayaquil')).strftime('%d de %B de %Y')

        facturas_data = []
        total_facturas = 0

        # Procesar cada factura
        for factura in facturas:
            informe = factura.id_informe  # Obtener el informe relacionado
            solicitud = informe.id_solicitud  # Obtener la solicitud relacionada
            empleado = solicitud.id_empleado.id_persona  # Obtener datos del empleado

            # Generar el código secuencial para esta solicitud
            secuencial = solicitud.generar_codigo_solicitud()

            # Calcular total de facturas
            total_facturas += factura.valor if factura.valor else 0

            # Preparar datos para cada factura
            facturas_data.append({
                'factura': factura,
                'secuencial': secuencial,
                'nombre_empleado': f"{empleado.nombres} {empleado.apellidos}",
                'motivo': solicitud.motivo_movilizacion,
                'acompanantes': solicitud.listado_empleado.split(',') if solicitud.listado_empleado else [],
                'fecha_informe': informe.fecha_salida_informe if informe else None
            })

        # Preparar contexto
        context = {
            'current_date': current_date,
            'facturas_data': facturas_data,
            'total_facturas': total_facturas
        }

        # Renderizar el HTML
        template_path = 'reporte_factura_viajes.html'
        html_content = render_to_string(template_path, context)

        # Generar PDF con WeasyPrint
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)

        # Crear respuesta HTTP con el PDF
        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="reporte_facturas.pdf"'

        return response
    except Exception as e:
        return HttpResponse(f'Error al generar el PDF: {str(e)}', status=500)

def generar_pdf_vacio(tipo_reporte):
    try:
        # Pasar el tipo de reporte a la plantilla
        context = {'tipo_reporte': tipo_reporte, 'current_date': datetime.now().strftime('%Y-%m-%d')}
        html_string = render_to_string('reporte_vacio.html', context)

        pdf_file = BytesIO()
        HTML(string=html_string).write_pdf(pdf_file)

        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="reporte_vacio.pdf"'
        response['Content-Transfer-Encoding'] = 'binary'

        return response

    except Exception as e:
        return HttpResponse(f'Error al generar el PDF vacío: {str(e)}', status=500)
