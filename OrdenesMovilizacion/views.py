from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import OrdenesMovilizacion

@method_decorator(csrf_exempt, name='dispatch')
class ListarOrdenMovilizacionView(View):
    def get(self, request, *args, **kwargs):
        try:
            ordenes = OrdenesMovilizacion.objects.all().values()
            return JsonResponse(list(ordenes), safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

import json

@method_decorator(csrf_exempt, name='dispatch')
class CrearOrdenMovilizacionView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            secuencial_orden = data.get('secuencial_orden_movilizacion')
            fecha_hora_emision = data.get('fecha_hora_emision')
            fecha_desde = data.get('fecha_desde')
            hora_desde = data.get('hora_desde')
            fecha_hasta = data.get('fecha_hasta')
            hora_hasta = data.get('hora_hasta')

            nueva_orden = OrdenesMovilizacion(
                secuencial_orden_movilizacion=secuencial_orden,
                fecha_hora_emision=fecha_hora_emision,
                fecha_desde=fecha_desde,
                hora_desde=hora_desde,
                fecha_hasta=fecha_hasta,
                hora_hasta=hora_hasta
            )
            nueva_orden.save()

            return JsonResponse({
                'id_orden_movilizacion': nueva_orden.id_orden_movilizacion,
                'secuencial_orden_movilizacion': nueva_orden.secuencial_orden_movilizacion,
                'fecha_hora_emision': nueva_orden.fecha_hora_emision,
                'fecha_desde': nueva_orden.fecha_desde,
                'hora_desde': nueva_orden.hora_desde,
                'fecha_hasta': nueva_orden.fecha_hasta,
                'hora_hasta': nueva_orden.hora_hasta,
                'habilitado': nueva_orden.habilitado
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EditarOrdenMovilizacionView(View):
    def post(self, request, id_orden, *args, **kwargs):
        try:
            orden = get_object_or_404(OrdenesMovilizacion, id_orden_movilizacion=id_orden)

            # Procesar el cuerpo de la solicitud JSON
            data = json.loads(request.body)
            orden.secuencial_orden_movilizacion = data.get('secuencial_orden_movilizacion', orden.secuencial_orden_movilizacion)
            orden.fecha_hora_emision = data.get('fecha_hora_emision', orden.fecha_hora_emision)
            orden.fecha_desde = data.get('fecha_desde', orden.fecha_desde)
            orden.hora_desde = data.get('hora_desde', orden.hora_desde)
            orden.fecha_hasta = data.get('fecha_hasta', orden.fecha_hasta)
            orden.hora_hasta = data.get('hora_hasta', orden.hora_hasta)

            orden.save()

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'secuencial_orden_movilizacion': orden.secuencial_orden_movilizacion,
                'fecha_hora_emision': orden.fecha_hora_emision,
                'fecha_desde': orden.fecha_desde,
                'hora_desde': orden.hora_desde,
                'fecha_hasta': orden.fecha_hasta,
                'hora_hasta': orden.hora_hasta,
                'habilitado': orden.habilitado
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CancelarOrdenMovilizacionView(View):
    def post(self, request, id_orden, *args, **kwargs):
        try:
            orden = get_object_or_404(OrdenesMovilizacion, id_orden_movilizacion=id_orden)
            orden.habilitado = 0  # Cambiar estado de habilitado a 0 para cancelar

            orden.save()

            return JsonResponse({
                'id_orden_movilizacion': orden.id_orden_movilizacion,
                'secuencial_orden_movilizacion': orden.secuencial_orden_movilizacion,
                'fecha_hora_emision': orden.fecha_hora_emision,
                'fecha_desde': orden.fecha_desde,
                'hora_desde': orden.hora_desde,
                'fecha_hasta': orden.fecha_hasta,
                'hora_hasta': orden.hora_hasta,
                'habilitado': orden.habilitado
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
