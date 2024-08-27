from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import jwt
from django.conf import settings
import re

from Bancos.models import Bancos
from Empleados.models import Usuarios

@method_decorator(csrf_exempt, name='dispatch')
class CrearBancoView(View):
    @transaction.atomic
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

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            nombre_banco = request.POST.get('nombre_banco')

            if not nombre_banco:
                return JsonResponse({'error': 'Nombre del banco no proporcionado'}, status=400)

            # Validación del nombre del banco permitiendo letras y acentos
            if not re.match(r'^[A-Za-zÀ-ÿ\s,]+$', nombre_banco):
                return JsonResponse({'error': 'El nombre del banco debe contener solo letras y acentos.'}, status=400)

            nombre_banco = nombre_banco.upper()  # Convertir a mayúsculas

            # Verificar si ya existe un banco con el mismo nombre
            if Bancos.objects.filter(nombre_banco=nombre_banco).exists():
                return JsonResponse({'error': 'Ya existe un banco con el mismo nombre.'}, status=400)

            # Crear el nuevo banco
            nuevo_banco = Bancos(
                nombre_banco=nombre_banco
            )
            nuevo_banco.save()

            return JsonResponse({
                'id_banco': nuevo_banco.id_banco,
                'nombre_banco': nuevo_banco.nombre_banco,
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            transaction.set_rollback(True)  # Asegura el rollback en caso de excepción
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarBancoView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_banco, *args, **kwargs):
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

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener el nombre del banco del request.POST
            nombre_banco = request.POST.get('nombre_banco')

            if not nombre_banco:
                return JsonResponse({'error': 'Nombre del banco no proporcionado'}, status=400)

            # Validación del nombre del banco permitiendo letras y acentos
            if not re.match(r'^[A-Za-zÀ-ÿ\s,]+$', nombre_banco):
                return JsonResponse({'error': 'El nombre del banco debe contener solo letras y acentos.'}, status=400)

            nombre_banco = nombre_banco.upper()  # Convertir a mayúsculas

            # Verificar si el banco existe
            try:
                banco = Bancos.objects.get(id_banco=id_banco)
            except Bancos.DoesNotExist:
                return JsonResponse({'error': 'Banco no encontrado'}, status=404)

            # Actualizar el banco
            banco.nombre_banco = nombre_banco
            banco.save()

            return JsonResponse({
                'id_banco': banco.id_banco,
                'nombre_banco': banco.nombre_banco,
            })

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Exception as e:
            transaction.set_rollback(True)  # Asegura el rollback en caso de excepción
            return JsonResponse({'error': str(e)}, status=500)