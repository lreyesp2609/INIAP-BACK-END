
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import jwt

from .models import Empleados, Personas, Unidades, Estaciones, Solicitudes, Informes, Usuarios,Bancos, Motivo,Provincias, Ciudades,Usuarios, Personas, Empleados, Cargos, Unidades
from datetime import datetime, date
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from .models import Solicitudes, Usuarios, Empleados
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Solicitudes, Usuarios, Empleados
from django.db.models import Max

from django.conf import settings
import jwt
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Func, Value, CharField
from django.views import View
from django.http import JsonResponse
from .models import Solicitudes, Empleados, Unidades, Usuarios

@method_decorator(csrf_exempt, name='dispatch')
class CrearSolicitudView(View):
    def incrementar_secuencia_solicitud(self, empleado):
        ultima_secuencia = Solicitudes.objects.filter(id_empleado=empleado).aggregate(Max('secuencia_solicitud'))
        ultima_secuencia_numero = ultima_secuencia['secuencia_solicitud__max']

        if ultima_secuencia_numero is not None:
            nueva_secuencia_numero = ultima_secuencia_numero + 1
        else:
            nueva_secuencia_numero = 1

        return nueva_secuencia_numero

    def post(self, request, id_usuario, *args, **kwargs):
        try:
            # Simular usuario y empleado para pruebas
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener datos del JSON enviado en el cuerpo del request
            data = json.loads(request.body)
            motivo_movilizacion = data.get('motivo_movilizacion', '')
            fecha_salida_solicitud = data.get('fecha_salida_solicitud', '')
            hora_salida_solicitud = data.get('hora_salida_solicitud', '')
            fecha_llegada_solicitud = data.get('fecha_llegada_solicitud', '')
            hora_llegada_solicitud = data.get('hora_llegada_solicitud', '')
            descripcion_actividades = data.get('descripcion_actividades', '')
            listado_empleado = data.get('listado_empleado', '')
            lugar_servicio = data.get('lugar_servicio', '')  # Nuevo campo lugar_servicio

            # Convertir las fechas de texto a objetos date si es necesario
            if fecha_salida_solicitud:
                fecha_salida_solicitud = datetime.strptime(fecha_salida_solicitud, '%Y-%m-%d').date()

            if fecha_llegada_solicitud:
                fecha_llegada_solicitud = datetime.strptime(fecha_llegada_solicitud, '%Y-%m-%d').date()

            # Generar secuencia_solicitud
            secuencia_solicitud = self.incrementar_secuencia_solicitud(empleado)

            # Crear la solicitud
            with transaction.atomic():
                solicitud = Solicitudes.objects.create(
                    secuencia_solicitud=secuencia_solicitud,
                    fecha_solicitud=date.today(),
                    motivo_movilizacion=motivo_movilizacion,
                    lugar_servicio=lugar_servicio,  # Agregar el lugar_servicio
                    fecha_salida_solicitud=fecha_salida_solicitud,
                    hora_salida_solicitud=hora_salida_solicitud,
                    fecha_llegada_solicitud=fecha_llegada_solicitud,
                    hora_llegada_solicitud=hora_llegada_solicitud,
                    descripcion_actividades=descripcion_actividades,
                    listado_empleado=listado_empleado,
                    estado_solicitud='pendiente',
                    id_empleado=empleado
                )

            return JsonResponse({'mensaje': 'Solicitud creada exitosamente', 'id_solicitud': solicitud.id_solicitud}, status=201)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'El usuario o el empleado no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        
class ListarSolicitudesView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener las solicitudes del empleado
            solicitudes = Solicitudes.objects.filter(id_empleado=empleado)

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                codigo_solicitud = solicitud.generar_codigo_solicitud()
                data.append({
                    'Codigo de Solicitud': codigo_solicitud,
                    'Fecha Solicitud': solicitud.fecha_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_solicitud else '',
                    'Motivo': solicitud.motivo_movilizacion if solicitud.motivo_movilizacion else '',
                    'Estado': solicitud.estado_solicitud if solicitud.estado_solicitud else '',
                })

            return JsonResponse({'solicitudes': data}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado correspondiente al usuario no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class ListarBancosView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todos los bancos
            bancos = Bancos.objects.all()

            # Preparar la respuesta con los nombres de los bancos
            data = [banco.nombre_banco for banco in bancos]

            return JsonResponse({'bancos': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ListarMotivosView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todos los motivos activos
            motivos = Motivo.objects.filter(estado_motivo=1)

            # Preparar la respuesta con los nombres de los motivos
            data = [motivo.nombre_motivo for motivo in motivos]

            return JsonResponse({'motivos': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class ListarProvinciaCiudadesView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todas las provincias
            provincias = Provincias.objects.all()

            # Preparar la respuesta con las provincias y ciudades relacionadas
            data = []
            for provincia in provincias:
                ciudades = Ciudades.objects.filter(id_provincia=provincia.id_provincia)
                ciudades_list = [ciudad.ciudad for ciudad in ciudades]
                data.append({
                    'Provincia': provincia.provincia,
                    'Ciudades': ciudades_list,
                })

            return JsonResponse({'provincias_ciudades': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        


class ListarDatosPersonalesView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario asociado a la id_usuario proporcionada en la URL
            usuario = Usuarios.objects.get(id_usuario=id_usuario)

            # Obtener la persona asociada al usuario
            persona = usuario.id_persona  # Accedemos directamente al campo id_persona del usuario

            # Obtener el empleado asociado a la persona
            empleado = Empleados.objects.get(id_persona=persona)

            # Obtener el cargo del empleado
            cargo = Cargos.objects.get(id_cargo=empleado.id_cargo_id)

            # Obtener la unidad asociada al cargo
            unidad = Unidades.objects.get(id_unidad=cargo.id_unidad_id)

            # Construir la respuesta con los datos requeridos
            datos_personales = {
                'Nombre': f"{empleado.distintivo} {persona.nombres} {persona.apellidos}",
                'Cargo': cargo.cargo,
                'Unidad': unidad.nombre_unidad,
            }

            return JsonResponse({'datos_personales': datos_personales}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe'}, status=404)

        except Personas.DoesNotExist:
            return JsonResponse({'error': 'La persona asociada al usuario no existe'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado asociado a la persona no existe'}, status=404)

        except Cargos.DoesNotExist:
            return JsonResponse({'error': 'El cargo asociado al empleado no existe'}, status=404)

        except Unidades.DoesNotExist:
            return JsonResponse({'error': 'La unidad asociada al cargo no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

class PrevisualizarCodigoSolicitudView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el empleado asociado al usuario
            empleado = Empleados.objects.get(id_persona_id=id_usuario)

            # Obtener la última secuencia de solicitud del empleado
            ultima_solicitud = Solicitudes.objects.filter(id_empleado=empleado).order_by('-secuencia_solicitud').first()

            # Obtener la secuencia actual y ajustarla para la previsualización
            if ultima_solicitud:
                secuencia_actual = ultima_solicitud.secuencia_solicitud + 1
            else:
                secuencia_actual = 1  # Si no hay solicitudes anteriores, empezamos en 1

            # Obtener datos para construir el código de solicitud
            persona = empleado.id_persona
            primer_apellido = persona.apellidos.split()[0] if persona.apellidos else ''
            segundo_apellido = persona.apellidos.split()[1][0] if len(persona.apellidos.split()) > 1 else ''
            primer_nombre = persona.nombres.split()[0] if persona.nombres else ''
            segundo_nombre = persona.nombres.split()[1][0] if len(persona.nombres.split()) > 1 else ''

            unidad = Unidades.objects.get(id_unidad=empleado.id_cargo.id_unidad_id)
            siglas_unidad = unidad.siglas_unidad if unidad.siglas_unidad else ''
            estacion = unidad.id_estacion
            siglas_estacion = estacion.siglas_estacion if estacion.siglas_estacion else ''

            year_solicitud = datetime.now().year

            # Construir el código de solicitud con la secuencia actualizada
            codigo_solicitud = f'{secuencia_actual:03}-{primer_apellido[0]}{segundo_apellido[0]}{primer_nombre[0]}{segundo_nombre[0]}-{siglas_unidad}-INIAP-{siglas_estacion}-{year_solicitud}'

            # Preparar la respuesta con los datos requeridos
            datos_previsualizacion = {
                'Codigo de Solicitud': codigo_solicitud,
                'Fecha y Hora de Previsualización': datetime.now().strftime('%d-%m-%Y'),
            }

            return JsonResponse({'previsualizacion': datos_previsualizacion}, status=200)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado correspondiente al usuario no existe'}, status=404)

        except Unidades.DoesNotExist:
            return JsonResponse({'error': 'La unidad asociada al empleado no existe'}, status=404)

        except Estaciones.DoesNotExist:
            return JsonResponse({'error': 'La estación asociada a la unidad no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class ListarEmpleadosView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todos los empleados
            empleados = Empleados.objects.all()

            # Preparar la respuesta con los datos de los empleados
            data = [
                {
                    'distintivo': emp.distintivo,
                    'nombres': emp.id_persona.nombres,
                    'apellidos': emp.id_persona.apellidos,
                }
                for emp in empleados
            ]

            return JsonResponse({'empleados': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

class ListarEmpleadoSesion(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario por id_usuario
            usuario = Usuarios.objects.get(pk=id_usuario)

            # Obtener la persona asociada al usuario
            persona = usuario.id_persona

            # Obtener el empleado asociado a la persona
            empleado = Empleados.objects.get(id_persona=persona)

            # Preparar la respuesta con los datos del empleado
            data = {
                'distintivo': empleado.distintivo,
                'nombres': empleado.id_persona.nombres,
                'apellidos': empleado.id_persona.apellidos,
            }

            return JsonResponse(data, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)