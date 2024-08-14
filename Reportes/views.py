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
from Empleados.urls import Empleados, Usuarios


@method_decorator(csrf_exempt, name='dispatch')
class GenerarReporteView(View):
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
            
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            nombre_empleado = request.GET.get('nombre_empleado')
            nombre_conductor = request.GET.get('nombre_conductor')
            id_vehiculo = request.GET.get('id_vehiculo')

            filtros = {}
            if fecha_inicio and fecha_fin:
                filtros['fecha_viaje__range'] = [fecha_inicio, fecha_fin]
            if nombre_empleado:
                empleado = Empleados.objects.filter(nombre__icontains=nombre_empleado).first()
                if empleado:
                    filtros['id_empleado'] = empleado
            if nombre_conductor:
                conductor = Empleados.objects.filter(nombre__icontains=nombre_conductor).first()
                if conductor:
                    filtros['id_conductor'] = conductor
            if id_vehiculo:
                filtros['id_vehiculo'] = id_vehiculo

            ordenes = OrdenesMovilizacion.objects.filter(**filtros)

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
    response['Content-Disposition'] = 'attachment; filename="reporte_ordenes.pdf"'
    response['Content-Transfer-Encoding'] = 'binary'

    template = render_to_string(template_path, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), result)
    if not pdf.err:
        response.write(result.getvalue())
        return response
    else:
        return HttpResponse('Error al generar el PDF', status=500)
