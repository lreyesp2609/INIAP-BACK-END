import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed
from django.db import transaction
from .models import *

@method_decorator(csrf_exempt, name='dispatch')
class NuevoEmpleadoView(View):
    @transaction.atomic
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

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

            existing_persona = Personas.objects.filter(numero_cedula=persona_data['numero_cedula']).first()
            if existing_persona:
                raise Exception('Ya existe una persona con este número de cédula')

            persona = Personas.objects.create(**persona_data)

            cargo_id = request.POST.get('id_cargo')
            cargo = Cargos.objects.get(id_cargo=cargo_id)

            empleado_data = {
                'id_persona': persona,
                'id_cargo': cargo,
                'fecha_ingreso': request.POST.get('fecha_ingreso'),
                'habilitado': request.POST.get('habilitado'),
            }
            empleado = Empleados.objects.create(**empleado_data)

            usuario_data = {
                'id_rol': usuario.id_rol,
                'id_persona': persona,
                'usuario': '',
                'contrasenia': '',
            }

            usuario_data['usuario'] = self.generate_username(persona.nombres, persona.apellidos)

            usuario = Usuarios.objects.create(**usuario_data)

            return JsonResponse({'mensaje': 'Empleado creado exitosamente', 'id_empleado': empleado.id_empleado, 'id_usuario': usuario.id_usuario}, status=201)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)

    def generate_username(self, nombres, apellidos):
        base_username = f"{nombres.split()[0].lower()}.{apellidos.split()[0].lower()}"
        similar_usernames = Usuarios.objects.filter(usuario__startswith=base_username).count()
        if similar_usernames > 0:
            base_username += str(similar_usernames + 1)
        return base_username


@method_decorator(csrf_exempt, name='dispatch')
class ListaEmpleadosView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            empleados = Empleados.objects.select_related('id_persona', 'id_cargo').all()
            
            empleados_list = []
            for empleado in empleados:
                persona = empleado.id_persona
                cargo = empleado.id_cargo

                unidad = Unidades.objects.get(id_unidad=cargo.id_unidad_id)
                estacion = Estaciones.objects.get(id_estacion=unidad.id_estacion_id)

                try:
                    usuario_empleado = Usuarios.objects.get(id_persona=persona)
                except Usuarios.DoesNotExist:
                    usuario_empleado = None

                empleado_data = {
                    'nombres': persona.nombres,
                    'apellidos': persona.apellidos,
                    'usuario': usuario_empleado.usuario if usuario_empleado else None,
                    'cargo': cargo.cargo,
                    'nombre_unidad': unidad.nombre_unidad,
                    'nombre_estacion': estacion.nombre_estacion
                }
                empleados_list.append(empleado_data)

            return JsonResponse(empleados_list, safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'No se encontraron empleados'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)