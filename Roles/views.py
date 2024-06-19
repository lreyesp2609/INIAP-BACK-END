from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import jwt
from django.conf import settings
from .models import Rol

@method_decorator(csrf_exempt, name='dispatch')
class ObtenerRolesView(View):
    def get(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token para obtener la información del usuario
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Verificar si el token es válido
            if not payload:
                return JsonResponse({'error': 'Token inválido'}, status=401)

            # Verificar si el usuario tiene el rol de SuperUsuario
            rol_usuario = payload.get('rol')
            if rol_usuario != 'SuperUsuario':
                return JsonResponse({'error': 'Acceso denegado, se requiere permisos de SuperUsuario'}, status=403)

            # Obtener todos los roles
            roles = Rol.objects.all()

            roles_data = []
            for rol in roles:
                rol_data = {
                    'id_rol': rol.id_rol,
                    'rol': rol.rol,
                    'descripcion': rol.descripcion,
                }
                roles_data.append(rol_data)

            return JsonResponse({'roles': roles_data})

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
