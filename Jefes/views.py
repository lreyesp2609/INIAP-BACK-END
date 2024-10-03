from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import jwt

from Empleados.models import *
from django.conf import settings

@method_decorator(csrf_exempt, name='dispatch')
class AsignarJefeUnidadView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            id_usuario = payload.get('id_usuario')

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            id_empleado = request.POST.get('id_empleado')
            if not id_empleado:
                return JsonResponse({'error': 'ID del empleado es requerido'}, status=400)

            empleado = Empleados.objects.select_related('id_cargo', 'id_persona').get(id_empleado=id_empleado)
            id_cargo = empleado.id_cargo_id
            cargo = Cargos.objects.get(id_cargo=id_cargo)
            id_unidad = cargo.id_unidad_id

            # Verificar si ya existe un jefe en la unidad
            jefe_actual = Empleados.objects.filter(id_cargo__id_unidad=id_unidad, es_jefe=True).select_related('id_persona').first()

            if jefe_actual:
                # Desmarcar al jefe actual
                jefe_actual.es_jefe = False
                jefe_actual.save()

                jefe_info = {
                    'nombres': jefe_actual.id_persona.nombres,
                    'apellidos': jefe_actual.id_persona.apellidos,
                    'cedula': jefe_actual.id_persona.numero_cedula,
                    'unidad': jefe_actual.id_cargo.id_unidad.nombre_unidad,
                }
                # Asignar al nuevo jefe
                empleado.es_jefe = True
                empleado.save()

                return JsonResponse({
                    'mensaje': 'Jefe de unidad reemplazado exitosamente',
                    'jefe_anterior': jefe_info,
                    'nuevo_jefe': {
                        'nombres': empleado.id_persona.nombres,
                        'apellidos': empleado.id_persona.apellidos,
                        'cedula': empleado.id_persona.numero_cedula,
                        'unidad': cargo.id_unidad.nombre_unidad,
                    }
                }, status=200)

            # Asignar al nuevo jefe si no hay ninguno actual
            empleado.es_jefe = True
            empleado.save()

            return JsonResponse({'mensaje': 'Jefe de unidad asignado exitosamente'}, status=200)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
        except Cargos.DoesNotExist:
            return JsonResponse({'error': 'Cargo no encontrado'}, status=404)
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AsignarDirectorEstacionView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            id_usuario = payload.get('id_usuario')

            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            id_empleado = request.POST.get('id_empleado')
            if not id_empleado:
                return JsonResponse({'error': 'ID del empleado es requerido'}, status=400)

            empleado = Empleados.objects.select_related('id_cargo', 'id_persona').get(id_empleado=id_empleado)
            id_cargo = empleado.id_cargo_id
            cargo = Cargos.objects.get(id_cargo=id_cargo)
            id_estacion = cargo.id_unidad.id_estacion_id

            # Verificar si ya existe un director en la estación
            director_actual = Empleados.objects.filter(id_cargo__id_unidad__id_estacion=id_estacion, es_director=True).select_related('id_persona').first()

            if director_actual:
                # Desmarcar al director actual
                director_actual.es_director = False
                director_actual.save()

                director_info = {
                    'nombres': director_actual.id_persona.nombres,
                    'apellidos': director_actual.id_persona.apellidos,
                    'cedula': director_actual.id_persona.numero_cedula,
                    'unidad': director_actual.id_cargo.id_unidad.nombre_unidad,
                }
                # Asignar al nuevo director
                empleado.es_director = True
                empleado.save()

                return JsonResponse({
                    'mensaje': 'Director de estación reemplazado exitosamente',
                    'director_anterior': director_info,
                    'nuevo_director': {
                        'nombres': empleado.id_persona.nombres,
                        'apellidos': empleado.id_persona.apellidos,
                        'cedula': empleado.id_persona.numero_cedula,
                        'unidad': cargo.id_unidad.nombre_unidad,
                    }
                }, status=200)

            # Asignar al nuevo director si no hay ninguno actual
            empleado.es_director = True
            empleado.save()

            return JsonResponse({'mensaje': 'Director de estación asignado exitosamente'}, status=200)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
        except Cargos.DoesNotExist:
            return JsonResponse({'error': 'Cargo no encontrado'}, status=404)
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=500)