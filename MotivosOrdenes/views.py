from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.db import transaction
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from Empleados.models import Usuarios
from MotivosOrdenes.models import Motivo
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class CreateMotivoView(View):
    @transaction.atomic
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el token de los headers
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            # Verificar que el rol sea 'SuperUsuario'
            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Verificar que el id_usuario del token coincide con el id_usuario en la URL
            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            # Obtener los datos del formulario
            nombre_motivo = request.POST.get('nombre_motivo', '').upper()
            descripcion_motivo = request.POST.get('descripcion_motivo', '').upper()

            # Validar los campos requeridos
            if not nombre_motivo or not descripcion_motivo:
                return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

            # Crear un nuevo Motivo
            motivo = Motivo(
                nombre_motivo=nombre_motivo,
                descripcion_motivo=descripcion_motivo,
                estado_motivo=1  # Siempre activo
            )
            motivo.save()

            return JsonResponse({'mensaje': 'Motivo creado exitosamente'}, status=201)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListMotivosView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el token de los headers
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol not in ['SuperUsuario', 'Administrador', 'Empleado']:
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            motivos = Motivo.objects.filter(estado_motivo=1).values('id_motivo', 'nombre_motivo', 'descripcion_motivo')

            return JsonResponse({'motivos': list(motivos)}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarMotivoView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_motivo, *args, **kwargs):
        try:
            # Obtener el token de los headers
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            # Verificar que el rol sea 'SuperUsuario'
            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Verificar que el id_usuario del token coincide con el id_usuario en la URL
            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            # Obtener los datos del formulario
            nombre_motivo = request.POST.get('nombre_motivo', '').upper()
            descripcion_motivo = request.POST.get('descripcion_motivo', '').upper()

            # Validar los campos requeridos
            if not nombre_motivo or not descripcion_motivo:
                return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

            # Verificar si el motivo existe
            try:
                motivo = Motivo.objects.get(id_motivo=id_motivo)
            except Motivo.DoesNotExist:
                return JsonResponse({'error': 'Motivo no encontrado'}, status=404)

            # Actualizar los datos del motivo
            motivo.nombre_motivo = nombre_motivo
            motivo.descripcion_motivo = descripcion_motivo
            motivo.save()

            return JsonResponse({'mensaje': 'Motivo actualizado exitosamente'}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)
