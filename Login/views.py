import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Usuarios, Personas, Rol
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
                usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=id_usuario)

                persona = usuario.id_persona
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

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
