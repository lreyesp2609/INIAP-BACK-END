import jwt
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed
from django.db import transaction

from Estaciones.models import Estaciones
from Unidades.models import Unidades
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

            numero_cedula = request.POST.get('numero_cedula')
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            genero = request.POST.get('genero')
            celular = request.POST.get('celular')
            direccion = request.POST.get('direccion')
            correo_electronico = request.POST.get('correo_electronico')
            distintivo = request.POST.get('distintivo')
            id_rol = request.POST.get('id_rol')
            id_cargo = request.POST.get('id_cargo')

            # Usa la fecha actual del servidor como fecha de ingreso
            fecha_ingreso = datetime.now().strftime('%Y-%m-%d')

            if not all([numero_cedula, nombres, apellidos, fecha_nacimiento, genero, celular, direccion, correo_electronico, distintivo, id_rol, id_cargo]):
                return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

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

            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s.]+$', distintivo):
                return JsonResponse({'error': 'El distintivo debe contener solo letras, tildes y espacios'}, status=400)

            if not distintivo.endswith('.'):
                distintivo += '.'

            def parse_date(date_str):
                for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
                    try:
                        return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                    except ValueError:
                        pass
                raise ValueError('Formato de fecha inválido')

            try:
                fecha_nacimiento = parse_date(fecha_nacimiento)
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=400)

            fecha_nacimiento_dt = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            edad = (datetime.now() - fecha_nacimiento_dt).days // 365
            if edad < 18:
                return JsonResponse({'error': 'El empleado debe ser mayor de 18 años'}, status=400)

            habilitado = '1'

            existing_persona = Personas.objects.filter(numero_cedula=numero_cedula).first()
            if existing_persona:
                raise Exception('Ya existe una persona con este número de cédula')

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

            cargo = Cargos.objects.get(id_cargo=id_cargo)
            rol = Rol.objects.get(id_rol=id_rol)

            empleado_data = {
                'id_persona': persona,
                'id_cargo': cargo,
                'distintivo': distintivo,
                'fecha_ingreso': fecha_ingreso,
                'habilitado': habilitado,
            }
            empleado = Empleados.objects.create(**empleado_data)

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
        similar_usernames = Usuarios.objects.filter(usuario__startswith=base_username).values_list('usuario', flat=True)

        if similar_usernames:
            nombre_parts = nombres.split()
            if len(nombre_parts) > 1:
                base_username += nombre_parts[1][0].lower()
            if base_username in similar_usernames:
                base_username += str(len(similar_usernames) + 1)

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

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            empleado_usuario = Empleados.objects.select_related('id_cargo').get(id_persona=usuario.id_persona)
            unidad_usuario = Unidades.objects.get(id_unidad=empleado_usuario.id_cargo.id_unidad_id)
            estacion_usuario = Estaciones.objects.get(id_estacion=unidad_usuario.id_estacion_id)

            # Filtrando empleados que están habilitados (habilitado=1)
            empleados = Empleados.objects.select_related('id_persona', 'id_cargo').filter(
                id_cargo__id_unidad__id_estacion=estacion_usuario.id_estacion, habilitado=1
            ).order_by('id_empleado')

            empleados_list = []
            for empleado in empleados:
                persona = empleado.id_persona
                cargo = empleado.id_cargo

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
class ListaEmpleadosDeshabilitadosView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            empleado_usuario = Empleados.objects.select_related('id_cargo').get(id_persona=usuario.id_persona)
            unidad_usuario = Unidades.objects.get(id_unidad=empleado_usuario.id_cargo.id_unidad_id)
            estacion_usuario = Estaciones.objects.get(id_estacion=unidad_usuario.id_estacion_id)

            # Filtrando empleados que están deshabilitados (habilitado=0)
            empleados = Empleados.objects.select_related('id_persona', 'id_cargo').filter(
                id_cargo__id_unidad__id_estacion=estacion_usuario.id_estacion, habilitado=0
            ).order_by('id_empleado')

            empleados_list = []
            for empleado in empleados:
                persona = empleado.id_persona
                cargo = empleado.id_cargo

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
            usuario_empleado = Empleados.objects.get(id_persona=usuario.id_persona)
            usuario_unidad = usuario_empleado.id_cargo.id_unidad
            usuario_estacion = usuario_unidad.id_estacion

            empleado_unidad = empleado.id_cargo.id_unidad
            empleado_estacion = empleado_unidad.id_estacion

            if usuario_estacion != empleado_estacion:
                return JsonResponse({'error': 'No puedes editar empleados de otra estación'}, status=403)

            persona = empleado.id_persona

            # Actualización del número de cédula
            nuevo_numero_cedula = request.POST.get('numero_cedula')
            if nuevo_numero_cedula and nuevo_numero_cedula != persona.numero_cedula:
                if not nuevo_numero_cedula.isdigit():
                    return JsonResponse({'error': 'El número de cédula debe contener solo números'}, status=400)

                existing_persona = Personas.objects.filter(numero_cedula=nuevo_numero_cedula).exclude(id_persona=persona.id_persona).first()
                if existing_persona:
                    return JsonResponse({'error': 'Ya existe una persona con este número de cédula'}, status=400)

                persona.numero_cedula = nuevo_numero_cedula

            persona.nombres = request.POST.get('nombres', persona.nombres)
            persona.apellidos = request.POST.get('apellidos', persona.apellidos)

            fecha_nacimiento_str = request.POST.get('fecha_nacimiento', persona.fecha_nacimiento)
            if fecha_nacimiento_str:
                try:
                    # Asegúrate de que fecha_nacimiento_str sea una cadena antes de parsear
                    if isinstance(fecha_nacimiento_str, str):
                        def parse_date(date_str):
                            for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
                                try:
                                    return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                                except ValueError:
                                    pass
                            raise ValueError('Formato de fecha inválido')

                        fecha_nacimiento_str = parse_date(fecha_nacimiento_str)
                        fecha_nacimiento_dt = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
                        edad = (datetime.now().date() - fecha_nacimiento_dt).days // 365
                        if edad < 18:
                            return JsonResponse({'error': 'El empleado debe ser mayor de 18 años'}, status=400)
                        persona.fecha_nacimiento = fecha_nacimiento_dt
                except ValueError as e:
                    return JsonResponse({'error': str(e)}, status=400)

            persona.genero = request.POST.get('genero', persona.genero)
            persona.celular = request.POST.get('celular', persona.celular)
            persona.direccion = request.POST.get('direccion', persona.direccion)
            persona.correo_electronico = request.POST.get('correo_electronico', persona.correo_electronico)

            if persona.nombres and not persona.nombres.replace(" ", "").isalpha():
                return JsonResponse({'error': 'El nombre debe contener solo letras'}, status=400)
            
            if persona.apellidos and not persona.apellidos.replace(" ", "").isalpha():
                return JsonResponse({'error': 'Los apellidos deben contener solo letras'}, status=400)
            
            if persona.genero and persona.genero not in ['Masculino', 'Femenino']:
                return JsonResponse({'error': 'El género debe ser Masculino o Femenino'}, status=400)
            
            if persona.celular:
                celular_pattern = r'^\+?\d[\d\s]{9,15}$'
                if not re.match(celular_pattern, persona.celular):
                    return JsonResponse({'error': 'El número de celular debe tener un formato válido'}, status=400)
            
            if persona.direccion and not re.match(r'^[a-zA-Z0-9\s,.\-áéíóúÁÉÍÓÚñÑ]+$', persona.direccion):
                return JsonResponse({'error': 'La dirección debe contener solo letras y números'}, status=400)

            if persona.nombres and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', persona.nombres):
                return JsonResponse({'error': 'El nombre debe contener solo letras, tildes y espacios'}, status=400)

            if persona.apellidos and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', persona.apellidos):
                return JsonResponse({'error': 'Los apellidos deben contener solo letras, tildes y espacios'}, status=400)

            persona.save()

            cargo_id = request.POST.get('id_cargo')
            if cargo_id:
                cargo = Cargos.objects.get(id_cargo=cargo_id)
                empleado.id_cargo = cargo

            rol_id = request.POST.get('id_rol')
            if rol_id:
                rol = Rol.objects.get(id_rol=rol_id)
                if usuario.id_rol.rol != 'SuperUsuario':
                    return JsonResponse({'error': 'No tienes permisos suficientes para cambiar el rol'}, status=403)

                usuario_a_actualizar = Usuarios.objects.get(id_persona=persona)
                usuario_a_actualizar.id_rol = rol
                usuario_a_actualizar.save()

            empleado.fecha_ingreso = request.POST.get('fecha_ingreso', empleado.fecha_ingreso)
            empleado.habilitado = request.POST.get('habilitado', empleado.habilitado)
            empleado.distintivo = request.POST.get('distintivo', empleado.distintivo)
            if empleado.distintivo and not empleado.distintivo.endswith('.'):
                empleado.distintivo += '.'
            empleado.save()

            nuevo_usuario = request.POST.get('usuario')
            if nuevo_usuario:
                if Usuarios.objects.filter(usuario=nuevo_usuario).exclude(id_persona=persona.id_persona).exists():
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

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario asociado con la persona no encontrado'}, status=404)

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

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario del token no coincide con el de la URL'}, status=403)

            usuario = Usuarios.objects.select_related('id_rol', 'id_persona').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            empleado = Empleados.objects.select_related('id_persona', 'id_cargo__id_unidad__id_estacion').get(id_empleado=id_empleado)
            persona = empleado.id_persona
            cargo = empleado.id_cargo

            try:
                usuario_empleado = Usuarios.objects.select_related('id_rol').get(id_persona=persona)
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

            rol_data = {
                'id_rol': usuario_empleado.id_rol.id_rol if usuario_empleado else None,
                'rol': usuario_empleado.id_rol.rol if usuario_empleado else None
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
                'rol': rol_data,
                'genero': persona.genero,
                'distintivo': empleado.distintivo,
            }

            return JsonResponse(empleado_data, safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Objeto no encontrado'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DeshabilitarEmpleadoView(View):
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

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            empleado = Empleados.objects.get(id_empleado=id_empleado)
            if empleado.habilitado == 0:
                return JsonResponse({'error': 'El empleado ya está deshabilitado'}, status=400)

            # Extraer motivo de la solicitud
            motivo = request.POST.get('motivo')
            if not motivo:
                return JsonResponse({'error': 'Motivo no proporcionado'}, status=400)

            # Deshabilitar empleado
            empleado.habilitado = 0
            empleado.save()

            # Registrar motivo en MotivoEmpleados
            MotivoEmpleados.objects.create(id_empleado=empleado, motivo=motivo)

            return JsonResponse({'mensaje': 'Empleado deshabilitado exitosamente'}, status=200)

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

# views.py

@method_decorator(csrf_exempt, name='dispatch')
class HabilitarEmpleadoView(View):
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

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=token_id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            if token_id_usuario != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            empleado = Empleados.objects.get(id_empleado=id_empleado)
            if empleado.habilitado == 1:
                return JsonResponse({'error': 'El empleado ya está habilitado'}, status=400)

            motivo = request.POST.get('motivo')
            if not motivo:
                return JsonResponse({'error': 'Motivo es requerido'}, status=400)

            empleado.habilitado = 1
            empleado.save()

            # Registrar el motivo en el modelo MotivoEmpleados
            MotivoEmpleados.objects.create(
                id_empleado=empleado,
                motivo=motivo,
            )

            return JsonResponse({'mensaje': 'Empleado habilitado exitosamente'}, status=200)

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
