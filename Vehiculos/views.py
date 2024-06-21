from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Vehiculo
import jwt
from django.conf import settings

@method_decorator(csrf_exempt, name='dispatch')
class VehiculosListView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el token del encabezado Authorization
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token para obtener la información del usuario
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expirado'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Token inválido'}, status=401)

            # Verificar si el usuario tiene el rol de SuperUsuario
            rol_usuario = payload.get('rol')
            if rol_usuario != 'SuperUsuario':
                return JsonResponse({'error': 'Acceso denegado, se requieren permisos de SuperUsuario'}, status=403)

            # Si llegamos aquí, el usuario tiene permisos de SuperUsuario, obtener vehículos
            vehiculos = Vehiculo.objects.all()

            vehiculos_data = []
            for vehiculo in vehiculos:
                vehiculo_data = {
                    'id_vehiculo': vehiculo.id_vehiculo,
                    'placa': vehiculo.placa,
                    'codigo_inventario': vehiculo.codigo_inventario,
                    'modelo': vehiculo.modelo,
                    'marca': vehiculo.marca,
                    'color_primario': vehiculo.color_primario,
                    'color_secundario': vehiculo.color_secundario,
                    'anio_fabricacion': vehiculo.anio_fabricacion,
                    'numero_motor': vehiculo.numero_motor,
                    'numero_chasis': vehiculo.numero_chasis,
                    'numero_matricula': vehiculo.numero_matricula,
                    'habilitado': vehiculo.habilitado,
                }
                vehiculos_data.append(vehiculo_data)

            return JsonResponse({'vehiculos': vehiculos_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
