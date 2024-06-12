import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout

@method_decorator(csrf_exempt, name='dispatch')
class IniciarSesionView(View):
    def generate_token(self, usuario):
        payload = {
            'id_usuario': usuario.id_usuario,
            'nombre_usuario': usuario.usuario,
            'rol': usuario.id_rol.rol,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token

    def post(self, request, *args, **kwargs):
        try:
            nombre_usuario = request.POST.get('usuario')
            contrasenia = request.POST.get('contrasenia')

            user = Usuarios.objects.select_related('id_rol').filter(usuario=nombre_usuario).first()

            if user is not None:
                if check_password(contrasenia, user.contrasenia):

                    request.user = user

                    token = self.generate_token(user)

                    return JsonResponse({'token': token, 'nombre_usuario': nombre_usuario, 'id_usuario': user.id_usuario})
                else:
                    return JsonResponse({'mensaje': 'Contraseña incorrecta'}, status=401)
            else:
                return JsonResponse({'mensaje': 'Credenciales incorrectas'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CerrarSesionView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Cerrar sesión
            logout(request)

            return JsonResponse({'mensaje': 'Sesión cerrada exitosamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ObtenerUsuarioView(View):
    def get(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token para obtener la información del usuario
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Extraer el id de usuario del payload
            id_usuario = payload.get('id_usuario')

            if id_usuario:
                # Obtener el usuario con roles y personas relacionadas
                usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=id_usuario)

                # Obtener la persona asociada al usuario
                persona = usuario.id_persona

                # Obtener el empleado asociado a la persona
                empleado = Empleados.objects.select_related('id_cargo', 'id_persona', 'id_cargo__id_unidad__id_estacion').get(id_persona=persona)

                # Obtener las unidades asociadas al empleado
                unidades = Unidades.objects.filter(id_estacion=empleado.id_cargo.id_unidad.id_estacion)

                unidades_data = []
                for unidad in unidades:
                    unidad_data = {
                        'id_unidad': unidad.id_unidad,
                        'nombre_unidad': unidad.nombre_unidad,
                        'siglas_unidad': unidad.siglas_unidad,
                    }

                    # Obtener los cargos asociados a la unidad
                    cargos = Cargos.objects.filter(id_unidad=unidad.id_unidad)
                    cargos_data = []
                    for cargo in cargos:
                        cargo_data = {
                            'id_cargo': cargo.id_cargo,
                            'cargo': cargo.cargo,
                        }
                        cargos_data.append(cargo_data)

                    unidad_data['cargos'] = cargos_data
                    unidades_data.append(unidad_data)

                usuario_data = {
                    'id_usuario': usuario.id_usuario,
                    'usuario': usuario.usuario,
                    'nombre': persona.nombres,
                    'apellido': persona.apellidos,
                    'fecha_nacimiento': persona.fecha_nacimiento,
                    'genero': persona.genero,
                    'celular': persona.celular,
                    'direccion': persona.direccion,
                    'correo_electronico': persona.correo_electronico,
                    'id_rol': usuario.id_rol.id_rol,
                    'rol': usuario.id_rol.rol,
                    'descripcion_rol': usuario.id_rol.descripcion,
                    'estacion': {
                        'id_estacion': empleado.id_cargo.id_unidad.id_estacion.id_estacion,
                        'nombre_estacion': empleado.id_cargo.id_unidad.id_estacion.nombre_estacion,
                        'siglas_estacion': empleado.id_cargo.id_unidad.id_estacion.siglas_estacion,
                        'ruc': empleado.id_cargo.id_unidad.id_estacion.ruc,
                        'direccion': empleado.id_cargo.id_unidad.id_estacion.direccion,
                        'telefono': empleado.id_cargo.id_unidad.id_estacion.telefono,
                    },
                    'unidades': unidades_data,
                }

                return JsonResponse({'usuario': usuario_data})
            else:
                return JsonResponse({'error': 'ID de usuario no encontrado en el token'}, status=400)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        except Personas.DoesNotExist:
            return JsonResponse({'error': 'Persona no encontrada'}, status=404)

        except Rol.DoesNotExist:
            return JsonResponse({'error': 'Rol no encontrado'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)

        except Unidades.DoesNotExist:
            return JsonResponse({'error': 'Unidades no encontradas'}, status=404)

        except Cargos.DoesNotExist:
            return JsonResponse({'error': 'Cargos no encontrados'}, status=404)

        except Estaciones.DoesNotExist:
            return JsonResponse({'error': 'Estaciones no encontradas'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)