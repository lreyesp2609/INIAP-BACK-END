from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from Empleados.models import Usuarios
from .models import *
# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class ListaAllCargos(View):
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            

            cargos = Cargos.objects.values('id_cargo', 'cargo')

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

@method_decorator(csrf_exempt, name='dispatch')
class CrearCargoView(View):
    def post(self, request, id_usuario, *args, **kwargs):
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

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            id_unidad = request.POST.get('id_unidad')
            cargo = request.POST.get('cargo')

            if not id_unidad:
                return JsonResponse({'error': 'ID de unidad no proporcionado'}, status=400)
            if not cargo:
                return JsonResponse({'error': 'Nombre del cargo no proporcionado'}, status=400)

            # Verificar si la unidad existe
            try:
                unidad = Unidades.objects.get(id_unidad=id_unidad)
            except Unidades.DoesNotExist:
                return JsonResponse({'error': 'Unidad no encontrada'}, status=404)

            # Crear el nuevo cargo
            nuevo_cargo = Cargos(
                id_unidad=unidad,
                cargo=cargo
            )
            nuevo_cargo.save()

            return JsonResponse({
                'id_cargo': nuevo_cargo.id_cargo,
                'id_unidad': nuevo_cargo.id_unidad.id_unidad,
                'cargo': nuevo_cargo.cargo
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CrearCargoView(View):
    def post(self, request, id_usuario, id_unidad, *args, **kwargs):
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

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            cargo = request.POST.get('cargo')
            if not cargo:
                return JsonResponse({'error': 'Nombre del cargo no proporcionado'}, status=400)

            # Verificar si la unidad existe
            try:
                unidad = Unidades.objects.get(id_unidad=id_unidad)
            except Unidades.DoesNotExist:
                return JsonResponse({'error': 'Unidad no encontrada'}, status=404)

            # Crear el nuevo cargo
            nuevo_cargo = Cargos(
                id_unidad=unidad,
                cargo=cargo
            )
            nuevo_cargo.save()

            return JsonResponse({
                'id_cargo': nuevo_cargo.id_cargo,
                'id_unidad': nuevo_cargo.id_unidad.id_unidad,
                'cargo': nuevo_cargo.cargo
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class ListaCargosPorUnidadView(View):
    def get(self, request, id_usuario, id_unidad, *args, **kwargs):
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

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Verificar si la unidad existe
            try:
                unidad = Unidades.objects.get(id_unidad=id_unidad)
            except Unidades.DoesNotExist:
                return JsonResponse({'error': 'Unidad no encontrada'}, status=404)

            # Obtener los cargos asociados a la unidad
            cargos = Cargos.objects.filter(id_unidad=id_unidad).values('id_cargo', 'cargo')

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
class EditarCargoView(View):
    def post(self, request, id_usuario, id_cargo, *args, **kwargs):
        try:
            # Autenticación por token
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

            # Obtener datos del formulario
            cargo = request.POST.get('cargo', '').upper()

            # Validar campos obligatorios
            if not cargo:
                return JsonResponse({'error': 'El nombre del cargo es requerido'}, status=400)

            # Verificar si ya existe un cargo con el mismo nombre en la misma unidad
            if Cargos.objects.filter(cargo=cargo, id_unidad=Cargos.objects.get(id_cargo=id_cargo).id_unidad).exclude(id_cargo=id_cargo).exists():
                return JsonResponse({'error': 'Ya existe un cargo con este nombre en la unidad'}, status=400)

            # Actualizar el cargo
            Cargos.objects.filter(id_cargo=id_cargo).update(
                cargo=cargo
            )

            return JsonResponse({'mensaje': 'Cargo actualizado exitosamente'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)