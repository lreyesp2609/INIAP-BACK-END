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
from Empleados.models import Empleados
from Vehiculos.models import Vehiculo


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
            vehiculo = request.POST.get('vehiculo')

            filtros = {}
            if fecha_inicio and fecha_fin:
                filtros['fecha_viaje__range'] = [fecha_inicio, fecha_fin]
            if empleado:
                filtros['id_empleado'] = empleado
            if conductor:
                filtros['id_conductor_id'] = conductor
            if vehiculo:
                filtros['id_vehiculo'] = vehiculo

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
                    'duracion_movilizacion': str(orden.duracion_movilizacion),
                    'conductor_nombre_completo': f"{conductor.nombres} {conductor.apellidos}",
                    'vehiculo_placa': vehiculo.placa,
                    'fecha_viaje': orden.fecha_viaje.strftime('%Y-%m-%d'),
                    'hora_ida': orden.hora_ida.strftime('%H:%M:%S'),
                    'hora_regreso': orden.hora_regreso.strftime('%H:%M:%S'),
                    'estado_movilizacion': orden.estado_movilizacion,
                    'empleado_nombre_completo': f"{empleado.nombres} {empleado.apellidos}",
                    'habilitado': orden.habilitado,
                })

            return generar_pdf(lista_ordenes)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            print(f'Error al generar el reporte: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)


def generar_pdf(ordenes):
    template_path = 'reporte_ordenes.html'
    context = {'ordenes': ordenes}
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
