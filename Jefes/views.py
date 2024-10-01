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

            # Decodificar el token JWT y verificar permisos
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            id_usuario = payload.get('id_usuario')

            # Verificar que el usuario tenga el rol adecuado
            usuario = Usuarios.objects.select_related('id_rol').get(id_usuario=id_usuario)
            if usuario.id_rol.rol != 'SuperUsuario':
                return JsonResponse({'error': 'No tienes permisos suficientes'}, status=403)

            id_empleado = request.POST.get('id_empleado')

            if not id_empleado:
                return JsonResponse({'error': 'ID del empleado es requerido'}, status=400)

            # Obtener el empleado y su cargo
            empleado = Empleados.objects.select_related('id_cargo').get(id_empleado=id_empleado)
            id_cargo = empleado.id_cargo_id

            # Obtener la unidad asociada al cargo
            cargo = Cargos.objects.get(id_cargo=id_cargo)
            id_unidad = cargo.id_unidad_id

            # Verificar que no haya otro jefe en la unidad
            Empleados.objects.filter(id_cargo=id_cargo, es_jefe=True).update(es_jefe=False)

            # Asignar al nuevo jefe
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
