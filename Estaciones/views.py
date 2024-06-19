from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import *

@method_decorator(csrf_exempt, name='dispatch')
class ListaCargosView(View):
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            estacion_id = request.POST.get('estacion_id')
            unidad_id = request.POST.get('unidad_id')

            cargos = Cargos.objects.filter(
                id_unidad__id_estacion=estacion_id, id_unidad=unidad_id
            ).values('id_cargo', 'cargo')

            return JsonResponse(list(cargos), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ListaEstacionesView(View):
    def get(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            estaciones = Estaciones.objects.all().values('id_estacion', 'nombre_estacion')

            return JsonResponse(list(estaciones), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListaUnidadesPorEstacionView(View):
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            estacion_id = request.POST.get('estacion_id')
            if not estacion_id:
                return JsonResponse({'error': 'ID de estación no proporcionado'}, status=400)

            unidades = Unidades.objects.filter(id_estacion=estacion_id).values('id_unidad', 'nombre_unidad', 'id_estacion_id')

            return JsonResponse(list(unidades), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListaCargosView2(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el token del encabezado
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar y verificar el token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Si el token es válido, continuar obteniendo los cargos
            cargos = Cargos.objects.all().values('id_cargo', 'cargo')

            return JsonResponse(list(cargos), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)