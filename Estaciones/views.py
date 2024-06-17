from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import Cargos

@method_decorator(csrf_exempt, name='dispatch')
class ListaCargosView(View):
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
