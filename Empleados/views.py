from django.shortcuts import render
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from .models import Usuarios, Personas, Cargos, Empleados

@method_decorator(csrf_exempt, name='dispatch')
class NuevoEmpleadoView(View):
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Obtener el id de usuario del payload
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            # Verificar si el usuario autenticado es SuperUsuario
            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Verificar que el id_usuario en la URL coincida con el id_usuario del token
            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            # Procesar la creación del empleado
            persona_data = {
                'numero_cedula': request.POST.get('numero_cedula'),
                'nombres': request.POST.get('nombres'),
                'apellidos': request.POST.get('apellidos'),
                'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                'genero': request.POST.get('genero'),
                'celular': request.POST.get('celular'),
                'direccion': request.POST.get('direccion'),
                'correo_electronico': request.POST.get('correo_electronico'),
            }
            persona = Personas.objects.create(**persona_data)

            cargo_id = request.POST.get('id_cargo')
            cargo = Cargos.objects.get(id_cargo=cargo_id)

            empleado_data = {
                'id_persona': persona,
                'id_cargo': cargo,
                'distrito': request.POST.get('distrito'),
                'fecha_ingreso': request.POST.get('fecha_ingreso'),
                'habilitado': request.POST.get('habilitado'),
            }
            empleado = Empleados.objects.create(**empleado_data)

            return JsonResponse({'mensaje': 'Empleado creado exitosamente', 'id_empleado': empleado.id_empleado}, status=201)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Personas.DoesNotExist:
            return JsonResponse({'error': 'Persona no encontrada'}, status=404)

        except Cargos.DoesNotExist:
            return JsonResponse({'error': 'Cargo no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
