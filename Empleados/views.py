import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed
from django.db import transaction
from .models import *
from django.contrib.auth.hashers import make_password
import re
from datetime import datetime

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

            # Validaciones de entrada
            numero_cedula = request.POST.get('numero_cedula')
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            genero = request.POST.get('genero')
            celular = request.POST.get('celular')
            direccion = request.POST.get('direccion')
            correo_electronico = request.POST.get('correo_electronico')
            distintivo = request.POST.get('distintivo')
            fecha_ingreso = request.POST.get('fecha_ingreso')
            habilitado = request.POST.get('habilitado')
            id_rol = request.POST.get('id_rol')  # Nuevo campo para el ID del rol

            if not all([numero_cedula, nombres, apellidos, fecha_nacimiento, genero, celular, direccion, correo_electronico, distintivo, fecha_ingreso, habilitado, id_rol]):
                return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

            # Validar formato de campos
            if not numero_cedula.isdigit():
                return JsonResponse({'error': 'El número de cédula debe contener solo números'}, status=400)

            if not nombres.replace(" ", "").isalpha():
                return JsonResponse({'error': 'El nombre debe contener solo letras'}, status=400)

            if not apellidos.replace(" ", "").isalpha():
                return JsonResponse({'error': 'Los apellidos deben contener solo letras'}, status=400)

            if not genero in ['Masculino', 'Femenino']:
                return JsonResponse({'error': 'El género debe ser Masculino o Femenino'}, status=400)

            celular_pattern = r'^\+?\d[\d\s]{9,15}$'
            if not re.match(celular_pattern, celular):
                return JsonResponse({'error': 'El número de celular debe tener un formato válido'}, status=400)
            
            if not re.match(r'^[a-zA-Z0-9\s,.\-áéíóúÁÉÍÓÚñÑ]+$', direccion):
                return JsonResponse({'error': 'La dirección debe contener solo letras y números'}, status=400)

            if not distintivo.isalpha():
                return JsonResponse({'error': 'El distintivo debe contener solo letras'}, status=400)

            # Convertir las fechas a formato YYYY-MM-DD
            def parse_date(date_str):
                for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
                    try:
                        return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                    except ValueError:
                        pass
                raise ValueError('Formato de fecha inválido')

            try:
                fecha_nacimiento = parse_date(fecha_nacimiento)
                fecha_ingreso = parse_date(fecha_ingreso)
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=400)

            # Validación adicional de fechas
            if fecha_nacimiento != '2002-09-26':
                return JsonResponse({'error': 'La fecha de nacimiento debe ser 2002-09-26'}, status=400)

            if fecha_ingreso != '2024-06-23':
                return JsonResponse({'error': 'La fecha de ingreso debe ser 2024-06-23'}, status=400)

            if habilitado not in ['0', '1']:
                return JsonResponse({'error': 'El campo habilitado debe ser 0 o 1'}, status=400)

            existing_persona = Personas.objects.filter(numero_cedula=numero_cedula).first()
            if existing_persona:
                raise Exception('Ya existe una persona con este número de cédula')

            # Crear la persona
            persona_data = {
                'numero_cedula': numero_cedula,
                'nombres': nombres,
                'apellidos': apellidos,
                'fecha_nacimiento': fecha_nacimiento,
                'genero': genero,
                'celular': celular,
                'direccion': direccion,
                'correo_electronico': correo_electronico,
            }
            persona = Personas.objects.create(**persona_data)

            # Obtener el cargo del empleado
            cargo_id = request.POST.get('id_cargo')
            cargo = Cargos.objects.get(id_cargo=cargo_id)

            # Crear el empleado
            empleado_data = {
                'id_persona': persona,
                'id_cargo': cargo,
                'distintivo': distintivo,
                'fecha_ingreso': fecha_ingreso,
                'habilitado': habilitado,
            }
            empleado = Empleados.objects.create(**empleado_data)

            # Obtener y asignar el rol del empleado
            rol = Rol.objects.get(id_rol=id_rol)
            empleado.id_rol = rol  # Asignar el rol al empleado
            empleado.save()

            # Crear el usuario asociado al empleado
            usuario_data = {
                'id_rol': rol,
                'id_persona': persona,
                'usuario': self.generate_username(persona.nombres, persona.apellidos),
                'contrasenia': make_password(persona.numero_cedula),
            }
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

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener la estación del usuario
            empleado_usuario = Empleados.objects.select_related('id_cargo').get(id_persona=usuario.id_persona)
            unidad_usuario = Unidades.objects.get(id_unidad=empleado_usuario.id_cargo.id_unidad_id)
            estacion_usuario = Estaciones.objects.get(id_estacion=unidad_usuario.id_estacion_id)

            # Obtener todos los empleados de la misma estación ordenados por id_empleado
            empleados = Empleados.objects.select_related('id_persona', 'id_cargo').filter(id_cargo__id_unidad__id_estacion=estacion_usuario.id_estacion).order_by('id_empleado')

            empleados_list = []
            for empleado in empleados:
                persona = empleado.id_persona
                cargo = empleado.id_cargo

                # Obtener el usuario asociado al empleado
                try:
                    usuario_empleado = Usuarios.objects.get(id_persona=persona)
                except Usuarios.DoesNotExist:
                    usuario_empleado = None

                empleado_data = {
                    'nombres': persona.nombres,
                    'apellidos': persona.apellidos,
                    'cedula': persona.numero_cedula,
                    'correo_electronico': persona.correo_electronico,
                    'fecha_nacimiento': persona.fecha_nacimiento,
                    'celular': persona.celular,
                    'cargo': cargo.cargo,
                    'nombre_unidad': cargo.id_unidad.nombre_unidad,
                    'nombre_estacion': cargo.id_unidad.id_estacion.nombre_estacion,
                    'id_empleado': empleado.id_empleado,
                    'fecha_ingreso': empleado.fecha_ingreso,
                    'direccion': persona.direccion,
                    'usuario': usuario_empleado.usuario if usuario_empleado else None,
                    'habilitado': empleado.habilitado,
                    'genero': persona.genero,
                    'distintivo': empleado.distintivo
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

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Objeto no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EditarEmpleadoView(View):
    @transaction.atomic
    def post(self, request, id_usuario, id_empleado, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            empleado = Empleados.objects.select_related('id_persona', 'id_cargo').get(id_empleado=id_empleado)

            # Obtener la unidad del cargo del usuario a través de la persona
            usuario_empleado = Empleados.objects.get(id_persona=usuario.id_persona)
            usuario_unidad = usuario_empleado.id_cargo.id_unidad
            usuario_estacion = usuario_unidad.id_estacion

            # Obtener la unidad del cargo del empleado
            empleado_unidad = empleado.id_cargo.id_unidad
            empleado_estacion = empleado_unidad.id_estacion

            if usuario_estacion != empleado_estacion:
                return JsonResponse({'error': 'No puedes editar empleados de otra estación'}, status=403)

            persona = empleado.id_persona

            # Validar si se está intentando cambiar el número de cédula
            nuevo_numero_cedula = request.POST.get('numero_cedula')
            if nuevo_numero_cedula and nuevo_numero_cedula != persona.numero_cedula:
                existing_persona = Personas.objects.filter(numero_cedula=nuevo_numero_cedula).exclude(id_persona=persona.id_persona).first()
                if existing_persona:
                    return JsonResponse({'error': 'Ya existe una persona con este número de cédula'}, status=400)

            # Actualizar los datos de la persona solo si no se cambia el número de cédula
            persona.numero_cedula = nuevo_numero_cedula or persona.numero_cedula
            persona.nombres = request.POST.get('nombres', persona.nombres)
            persona.apellidos = request.POST.get('apellidos', persona.apellidos)
            persona.fecha_nacimiento = request.POST.get('fecha_nacimiento', persona.fecha_nacimiento)
            persona.genero = request.POST.get('genero', persona.genero)
            persona.celular = request.POST.get('celular', persona.celular)
            persona.direccion = request.POST.get('direccion', persona.direccion)
            persona.correo_electronico = request.POST.get('correo_electronico', persona.correo_electronico)
            persona.save()

            cargo_id = request.POST.get('id_cargo')
            if cargo_id:
                cargo = Cargos.objects.get(id_cargo=cargo_id)
                empleado.id_cargo = cargo

            empleado.fecha_ingreso = request.POST.get('fecha_ingreso', empleado.fecha_ingreso)
            empleado.habilitado = request.POST.get('habilitado', empleado.habilitado)
            empleado.distintivo = request.POST.get('distintivo', empleado.distintivo)
            empleado.save()

            # Validar y actualizar el nombre de usuario
            nuevo_usuario = request.POST.get('usuario')
            if nuevo_usuario:
                existing_usuario = Usuarios.objects.filter(usuario=nuevo_usuario).exclude(id_persona=persona.id_persona).first()
                if existing_usuario:
                    return JsonResponse({'error': 'El nombre de usuario ya existe'}, status=400)

                usuario_empleado = Usuarios.objects.get(id_persona=persona)
                usuario_empleado.usuario = nuevo_usuario
                usuario_empleado.save()

            return JsonResponse({'mensaje': 'Empleado editado exitosamente'}, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)

        
@method_decorator(csrf_exempt, name='dispatch')
class DetalleEmpleadoView(View):
    def get(self, request, id_usuario, id_empleado, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            # Obtener el empleado solicitado
            empleado = Empleados.objects.select_related('id_persona', 'id_cargo__id_unidad__id_estacion').get(id_empleado=id_empleado)
            persona = empleado.id_persona
            cargo = empleado.id_cargo

            # Obtener el usuario asociado al empleado
            try:
                usuario_empleado = Usuarios.objects.get(id_persona=persona)
            except Usuarios.DoesNotExist:
                usuario_empleado = None
                
            cargo_data = {
                'id_cargo': cargo.id_cargo,
                'cargo': cargo.cargo
            }

            unidad_data = {
                'id_unidad': cargo.id_unidad.id_unidad,
                'unidad': cargo.id_unidad.nombre_unidad
            }

            estacion_data = {
                'id_estacion': cargo.id_unidad.id_estacion.id_estacion,
                'estacion': cargo.id_unidad.id_estacion.nombre_estacion
            }
            
            empleado_data = {
                'nombres': persona.nombres,
                'apellidos': persona.apellidos,
                'cedula': persona.numero_cedula,
                'correo_electronico': persona.correo_electronico,
                'fecha_nacimiento': persona.fecha_nacimiento,
                'celular': persona.celular,
                'cargo': cargo_data,
                'unidad': unidad_data,
                'estacion': estacion_data,
                'id_empleado': empleado.id_empleado,
                'fecha_ingreso': empleado.fecha_ingreso,
                'direccion': persona.direccion,
                'usuario': usuario_empleado.usuario if usuario_empleado else None,
                'habilitado': empleado.habilitado,
                'id_rol': usuario_empleado.id_rol.id_rol if usuario_empleado else None,
                'genero': persona.genero,
                'distintivo': empleado.distintivo,
            }

            return JsonResponse(empleado_data, safe=False)

        except ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Objeto no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
