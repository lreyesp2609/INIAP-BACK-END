from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import *
import jwt
from django.conf import settings
# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class ListarCiudadesPorProvinciaView(View):
    @transaction.atomic
    def get(self, request, id_usuario, id_provincia, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

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

            # Verificar si la provincia existe
            if not Provincias.objects.filter(id_provincia=id_provincia).exists():
                return JsonResponse({'error': 'Provincia no encontrada'}, status=404)

            # Obtener las ciudades de la provincia
            ciudades = Ciudades.objects.filter(id_provincia=id_provincia).values('id_ciudad', 'ciudad')

            return JsonResponse(list(ciudades), safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)
