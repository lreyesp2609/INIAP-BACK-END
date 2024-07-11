
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import jwt

from .models import Empleados, Personas, Unidades, Estaciones, Solicitudes, Informes, Usuarios
from datetime import datetime
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from .models import Solicitudes, Usuarios, Empleados
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Solicitudes, Usuarios, Empleados
from django.db.models import Max

from django.conf import settings
import jwt

from django.db.models import F, Func, Value, CharField
from django.views import View
from django.http import JsonResponse
from .models import Solicitudes, Empleados, Unidades, Usuarios

@method_decorator(csrf_exempt, name='dispatch')
class CrearSolicitudView(View):
    def incrementar_secuencia_solicitud(self, empleado):
        ultima_secuencia = Solicitudes.objects.filter(id_empleado=empleado).aggregate(Max('secuencia_solicitud'))
        ultima_secuencia_numero = ultima_secuencia['secuencia_solicitud__max']

        if ultima_secuencia_numero is not None:
            nueva_secuencia_numero = ultima_secuencia_numero + 1
        else:
            nueva_secuencia_numero = 1

        return f'{nueva_secuencia_numero:03}'

    def post(self, request, id_usuario, *args, **kwargs):
        try:
            # Simular usuario y empleado para pruebas
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener datos del formulario FormData
            fecha_solicitud = request.POST.get('fecha_solicitud')
            motivo_movilizacion = request.POST.get('motivo_movilizacion', '')
            fecha_salida_solicitud = request.POST.get('fecha_salida_solicitud', '')
            hora_salida_solicitud = request.POST.get('hora_salida_solicitud', '')
            fecha_llegada_solicitud = request.POST.get('fecha_llegada_solicitud', '')
            hora_llegada_solicitud = request.POST.get('hora_llegada_solicitud', '')
            descripcion_actividades = request.POST.get('descripcion_actividades', '')
            listado_empleado = request.POST.get('listado_empleado', '')

            # Generar secuencia_solicitud
            secuencia_solicitud = self.incrementar_secuencia_solicitud(empleado)

            # Crear la solicitud
            with transaction.atomic():
                solicitud = Solicitudes.objects.create(
                    secuencia_solicitud=secuencia_solicitud,
                    fecha_solicitud=fecha_solicitud,
                    motivo_movilizacion=motivo_movilizacion,
                    fecha_salida_solicitud=fecha_salida_solicitud,
                    hora_salida_solicitud=hora_salida_solicitud,
                    fecha_llegada_solicitud=fecha_llegada_solicitud,
                    hora_llegada_solicitud=hora_llegada_solicitud,
                    descripcion_actividades=descripcion_actividades,
                    listado_empleado=listado_empleado,
                    estado_solicitud='pendiente',
                    id_empleado=empleado
                )

            return JsonResponse({'mensaje': 'Solicitud creada exitosamente', 'id_solicitud': solicitud.id_solicitud}, status=201)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado correspondiente al usuario no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ListarSolicitudesView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener las solicitudes del empleado
            solicitudes = Solicitudes.objects.filter(id_empleado=empleado)

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                codigo_solicitud = solicitud.generar_codigo_solicitud()
                data.append({
                    'Codigo de Solicitud': codigo_solicitud,
                    'Fecha Solicitud': solicitud.fecha_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_solicitud else '',
                    'Motivo': solicitud.motivo_movilizacion if solicitud.motivo_movilizacion else '',
                    'Estado': solicitud.estado_solicitud if solicitud.estado_solicitud else '',
                })

            return JsonResponse({'solicitudes': data}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado correspondiente al usuario no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)