from django.conf import settings
from django.forms import ValidationError
from django.shortcuts import render
from django.http import JsonResponse
import jwt
from dateutil import parser

from Encabezados.models import Encabezados

from .models import Empleados, Personas, ProductosAlcanzadosInformes, TransporteInforme, Unidades, Estaciones, Solicitudes, Informes, Usuarios,Bancos, Motivo,Provincias, Ciudades,Usuarios, Personas, Empleados, Cargos, Unidades, TransporteSolicitudes, Vehiculo, CuentasBancarias,FacturasInformes, TotalFactura,EstadoFactura,MotivoCancelado
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
from django.utils.dateparse import parse_date, parse_time
from django.utils import timezone
from django.db.models import Sum

from django.db import transaction

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO

@method_decorator(csrf_exempt, name='dispatch')
class CrearSolicitudView(View):
    def incrementar_secuencia_solicitud(self, empleado):
        ultima_secuencia = Solicitudes.objects.filter(id_empleado=empleado).aggregate(Max('secuencia_solicitud'))
        ultima_secuencia_numero = ultima_secuencia['secuencia_solicitud__max']
        return (ultima_secuencia_numero or 0) + 1

    def post(self, request, id_usuario, *args, **kwargs):
        try:
            data = json.loads(request.body)
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener y validar los datos principales
            motivo_movilizacion = data.get('motivo_movilizacion', '')
            fecha_salida_solicitud = parse_date(data.get('fecha_salida_solicitud'))
            hora_salida_solicitud = parse_time(data.get('hora_salida_solicitud'))
            fecha_llegada_solicitud = parse_date(data.get('fecha_llegada_solicitud'))
            hora_llegada_solicitud = parse_time(data.get('hora_llegada_solicitud'))
            descripcion_actividades = data.get('descripcion_actividades', '')
            listado_empleado = data.get('listado_empleado', '')
            lugar_servicio = data.get('lugar_servicio', '')

            if not all([fecha_salida_solicitud, hora_salida_solicitud, fecha_llegada_solicitud, hora_llegada_solicitud]):
                return JsonResponse({'error': 'Fechas y horas de solicitud son requeridas y deben ser válidas'}, status=400)

            # Generar secuencia_solicitud
            secuencia_solicitud = self.incrementar_secuencia_solicitud(empleado)

            # Crear la solicitud y las solicitudes de transporte dentro de una transacción atómica
            with transaction.atomic():
                solicitud = Solicitudes.objects.create(
                    secuencia_solicitud=secuencia_solicitud,
                    fecha_solicitud=date.today(),
                    motivo_movilizacion=motivo_movilizacion,
                    lugar_servicio=lugar_servicio,
                    fecha_salida_solicitud=fecha_salida_solicitud,
                    hora_salida_solicitud=hora_salida_solicitud,
                    fecha_llegada_solicitud=fecha_llegada_solicitud,
                    hora_llegada_solicitud=hora_llegada_solicitud,
                    descripcion_actividades=descripcion_actividades,
                    listado_empleado=listado_empleado,
                    estado_solicitud='pendiente',
                    id_empleado=empleado
                )

                rutas = data.get('rutas', [])
                for ruta in rutas:
                    fecha_salida_soli = parse_date(ruta.get('fecha_salida_soli'))
                    hora_salida_soli = parse_time(ruta.get('hora_salida_soli'))
                    fecha_llegada_soli = parse_date(ruta.get('fecha_llegada_soli'))
                    hora_llegada_soli = parse_time(ruta.get('hora_llegada_soli'))

                    if not all([fecha_salida_soli, hora_salida_soli, fecha_llegada_soli, hora_llegada_soli]):
                        raise ValueError('Fechas y horas de ruta inválidas')

                    TransporteSolicitudes.objects.create(
                        id_solicitud=solicitud,
                        tipo_transporte_soli=ruta.get('tipo_transporte_soli'),
                        nombre_transporte_soli=ruta.get('nombre_transporte_soli'),
                        ruta_soli=f"{ruta.get('ciudad_origen')} - {ruta.get('ciudad_destino')}",
                        fecha_salida_soli=fecha_salida_soli,
                        hora_salida_soli=hora_salida_soli,
                        fecha_llegada_soli=fecha_llegada_soli,
                        hora_llegada_soli=hora_llegada_soli
                    )
                
                # Crear la cuenta bancaria siempre
                banco_id = data.get('id_banco')
                tipo_cuenta = data.get('tipo_cuenta')
                numero_cuenta = data.get('numero_cuenta')

                if not all([banco_id, tipo_cuenta, numero_cuenta]):
                    return JsonResponse({'error': 'Datos bancarios incompletos'}, status=400)

                try:
                    banco = Bancos.objects.get(id_banco=banco_id)
                    CuentasBancarias.objects.create(
                        id_banco=banco,
                        id_empleado=empleado,
                        id_solicitud=solicitud,
                        tipo_cuenta=tipo_cuenta,
                        numero_cuenta=numero_cuenta,
                        habilitado=1
                    )
                except ObjectDoesNotExist:
                    return JsonResponse({'error': 'El banco especificado no existe'}, status=400)

            return JsonResponse({
                'mensaje': 'Solicitud, solicitudes de transporte y cuenta bancaria creadas exitosamente',
                'id_solicitud': solicitud.id_solicitud
            }, status=201)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'El usuario o el empleado no existe'}, status=404)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error al crear la solicitud: {str(e)}'}, status=500)


class ListarSolicitudesView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener las solicitudes del empleado con estado pendiente
            solicitudes = Solicitudes.objects.filter(id_empleado=empleado, estado_solicitud='pendiente')

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                codigo_solicitud = solicitud.generar_codigo_solicitud()
                data.append({
                    'id':solicitud.id_solicitud,
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


class ListarSolicitudesAceptadasView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener las solicitudes del empleado con estado pendiente
            solicitudes = Solicitudes.objects.filter(id_empleado=empleado, estado_solicitud='aceptado')

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                codigo_solicitud = solicitud.generar_codigo_solicitud()
                data.append({
                    'id':solicitud.id_solicitud,
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
 
        
class ListarSolicitudesCanceladasView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener las solicitudes del empleado con estado pendiente
            solicitudes = Solicitudes.objects.filter(id_empleado=empleado, estado_solicitud='cancelado')

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                codigo_solicitud = solicitud.generar_codigo_solicitud()
                data.append({
                    'id':solicitud.id_solicitud,
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
                    'id': emp.id_empleado,
                    'distintivo': emp.distintivo,
                    'nombres': emp.id_persona.nombres,
                    'apellidos': emp.id_persona.apellidos,
                }
                for emp in empleados
            ]

            return JsonResponse({'empleados': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class ListarEmpleadoSesionView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario correspondiente
            usuario = Usuarios.objects.get(id_usuario=id_usuario)

            # Obtener la id_persona del usuario
            id_persona = usuario.id_persona.id_persona

            # Obtener el empleado correspondiente a la id_persona
            empleado = Empleados.objects.get(id_persona=id_persona)

            # Preparar la respuesta con los datos del empleado
            data = {
                'id': empleado.id_empleado,
                'distintivo': empleado.distintivo,
                'nombres': empleado.id_persona.nombres,
                'apellidos': empleado.id_persona.apellidos,
            }

            return JsonResponse({'empleado': data}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ListarNombreVehiculosView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todos los vehículos habilitados (habilitado = 1)
            vehiculos = Vehiculo.objects.filter(habilitado=1)

            # Preparar la respuesta con los datos de los vehículos
            data = [
                {
                    'placa': veh.placa,
                    'habilitado': veh.habilitado,
                }
                for veh in vehiculos
            ]

            return JsonResponse({'vehiculos': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ListarBancosView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todos los bancos ordenados por ID en orden ascendente
            bancos = Bancos.objects.all().order_by('id_banco')

            # Preparar la respuesta con los nombres e IDs de los bancos
            data = [{'id_banco': banco.id_banco, 'nombre_banco': banco.nombre_banco} for banco in bancos]

            return JsonResponse({'bancos': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CrearCuentaBancariaView(View):
    def post(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener datos de la solicitud desde form-data
            id_banco = request.POST.get('id_banco')
            tipo_cuenta = request.POST.get('tipo_cuenta')
            numero_cuenta = request.POST.get('numero_cuenta')
            habilitado = request.POST.get('habilitado', 1)  # Asignar 1 por defecto si no se proporciona
            id_solicitud = request.POST.get('id_solicitud')

            # Verificar que el banco y la solicitud existan
            if not Bancos.objects.filter(id_banco=id_banco).exists():
                return JsonResponse({'error': 'El banco no existe'}, status=404)
            if id_solicitud and not Solicitudes.objects.filter(id_solicitud=id_solicitud).exists():
                return JsonResponse({'error': 'La solicitud no existe'}, status=404)

            # Crear la cuenta bancaria
            with transaction.atomic():
                cuenta_bancaria = CuentasBancarias.objects.create(
                    id_banco_id=id_banco,
                    id_empleado=empleado,
                    id_solicitud_id=id_solicitud if id_solicitud else None,
                    tipo_cuenta=tipo_cuenta,
                    numero_cuenta=numero_cuenta,
                    habilitado=habilitado
                )

            return JsonResponse({
                'mensaje': 'Cuenta bancaria creada exitosamente',
                'id_cuenta_bancaria': cuenta_bancaria.id_cuenta_bancaria
            }, status=201)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'El usuario o el empleado no existe'}, status=404)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error al crear la cuenta bancaria: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ListarSolicitudesPendientesAdminView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener la persona asociada al administrador en sesión
            administrador = Usuarios.objects.get(id_usuario=id_usuario)
            persona_admin = administrador.id_persona

            # Obtener el empleado asociado a esa persona
            empleado_admin = Empleados.objects.get(id_persona=persona_admin)

            # Obtener la unidad del administrador a través de su cargo
            unidad_admin = empleado_admin.id_cargo.id_unidad

            # Filtrar las solicitudes pendientes que correspondan a empleados de la misma unidad
            solicitudes = Solicitudes.objects.filter(
                estado_solicitud='pendiente',
                id_empleado__id_cargo__id_unidad=unidad_admin
            )

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                codigo_solicitud = solicitud.generar_codigo_solicitud()
                data.append({
                    'id': solicitud.id_solicitud,
                    'Codigo de Solicitud': codigo_solicitud,
                    'Fecha Solicitud': solicitud.fecha_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_solicitud else '',
                    'Motivo': solicitud.motivo_movilizacion if solicitud.motivo_movilizacion else '',
                    'Estado': solicitud.estado_solicitud if solicitud.estado_solicitud else '',
                })

            return JsonResponse({'solicitudes': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ListarSolicitudesCanceladasAdminView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener la persona asociada al administrador en sesión
            administrador = Usuarios.objects.get(id_usuario=id_usuario)
            persona_admin = administrador.id_persona

            # Obtener el empleado asociado a esa persona
            empleado_admin = Empleados.objects.get(id_persona=persona_admin)

            # Obtener la unidad del administrador a través de su cargo
            unidad_admin = empleado_admin.id_cargo.id_unidad

            # Filtrar las solicitudes canceladas que correspondan a empleados de la misma unidad
            solicitudes = Solicitudes.objects.filter(
                estado_solicitud='cancelado',
                id_empleado__id_cargo__id_unidad=unidad_admin
            )

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                codigo_solicitud = solicitud.generar_codigo_solicitud()
                data.append({
                    'id': solicitud.id_solicitud,
                    'Codigo de Solicitud': codigo_solicitud,
                    'Fecha Solicitud': solicitud.fecha_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_solicitud else '',
                    'Motivo': solicitud.motivo_movilizacion if solicitud.motivo_movilizacion else '',
                    'Estado': solicitud.estado_solicitud if solicitud.estado_solicitud else '',
                })

            return JsonResponse({'solicitudes': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

@method_decorator(csrf_exempt, name='dispatch')
class ListarSolicitudesAceptadasAdminView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener la persona asociada al administrador en sesión
            administrador = Usuarios.objects.get(id_usuario=id_usuario)
            persona_admin = administrador.id_persona

            # Obtener el empleado asociado a esa persona
            empleado_admin = Empleados.objects.get(id_persona=persona_admin)

            # Obtener la unidad del administrador a través de su cargo
            unidad_admin = empleado_admin.id_cargo.id_unidad

            # Filtrar las solicitudes aceptadas que correspondan a empleados de la misma unidad
            solicitudes = Solicitudes.objects.filter(
                estado_solicitud='aceptado',
                id_empleado__id_cargo__id_unidad=unidad_admin
            )

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                try:
                    # Manejar el formateo de fecha
                    fecha_solicitud = solicitud.fecha_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_solicitud else ''
                except Exception as e:
                    fecha_solicitud = f"Error formateando fecha: {e}"

                try:
                    # Generar código de solicitud
                    codigo_solicitud = solicitud.generar_codigo_solicitud()
                except Exception as e:
                    codigo_solicitud = f"Error generando código: {e}"

                data.append({
                    'id': solicitud.id_solicitud,
                    'Codigo de Solicitud': codigo_solicitud if codigo_solicitud else '',
                    'Fecha Solicitud': fecha_solicitud,
                    'Motivo': solicitud.motivo_movilizacion if solicitud.motivo_movilizacion else '',
                    'Estado': solicitud.estado_solicitud if solicitud.estado_solicitud else '',
                })

            return JsonResponse({'solicitudes': data}, status=200)

        except Exception as e:
            import traceback
            error_message = traceback.format_exc()
            return JsonResponse({'error': error_message}, status=500)
        
class ListarSolicitudesEmpleadoView(View):
    def get(self, request, id_solicitud, *args, **kwargs):
        try:
            # Obtener la solicitud
            solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)
            empleado = solicitud.id_empleado

            # Obtener el usuario asociado al empleado
            usuario = Usuarios.objects.get(id_persona=empleado.id_persona)

            # Obtener la persona asociada al usuario
            persona = usuario.id_persona

            # Obtener el cargo del empleado
            cargo = Cargos.objects.get(id_cargo=empleado.id_cargo_id)

            # Obtener la unidad asociada al cargo
            unidad = Unidades.objects.get(id_unidad=cargo.id_unidad_id)

            # Obtener todas las rutas asociadas a la solicitud
            rutas = TransporteSolicitudes.objects.filter(id_solicitud=id_solicitud)

            # Obtener la cuenta bancaria asociada a la solicitud
            cuenta_bancaria = CuentasBancarias.objects.filter(id_solicitud=id_solicitud).first()
            banco = cuenta_bancaria.id_banco if cuenta_bancaria else None

            # Preparar la respuesta con los datos de la solicitud
            solicitud_data = {
                'Codigo de Solicitud': solicitud.generar_codigo_solicitud(),
                'Fecha Solicitud': solicitud.fecha_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_solicitud else '',
                'Motivo': solicitud.motivo_movilizacion if solicitud.motivo_movilizacion else '',
                'Lugar de Servicio': solicitud.lugar_servicio if solicitud.lugar_servicio else '',
                'Fecha de Salida': solicitud.fecha_salida_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_salida_solicitud else '',
                'Hora de Salida': solicitud.hora_salida_solicitud.strftime('%H:%M:%S') if solicitud.hora_salida_solicitud else '',
                'Fecha de Llegada': solicitud.fecha_llegada_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_llegada_solicitud else '',
                'Hora de Llegada': solicitud.hora_llegada_solicitud.strftime('%H:%M:%S') if solicitud.hora_llegada_solicitud else '',
                'Descripción de Actividades': solicitud.descripcion_actividades if solicitud.descripcion_actividades else '',
                'Listado de Empleados': solicitud.listado_empleado if solicitud.listado_empleado else ''
            }

            # Preparar la respuesta con los datos personales
            datos_personales = {
                'Nombre': f"{empleado.distintivo} {persona.nombres} {persona.apellidos}",
                'Cargo': cargo.cargo,
                'Unidad': unidad.nombre_unidad,
            }

            # Preparar la respuesta con los datos de las rutas
            rutas_data = []
            for ruta in rutas:
                rutas_data.append({
                    'Tipo de Transporte': ruta.tipo_transporte_soli if ruta.tipo_transporte_soli else '',
                    'Nombre del Transporte': ruta.nombre_transporte_soli if ruta.nombre_transporte_soli else '',
                    'Ruta': ruta.ruta_soli if ruta.ruta_soli else '',
                    'Fecha de Salida': ruta.fecha_salida_soli.strftime('%Y-%m-%d') if ruta.fecha_salida_soli else '',
                    'Hora de Salida': ruta.hora_salida_soli.strftime('%H:%M:%S') if ruta.hora_salida_soli else '',
                    'Fecha de Llegada': ruta.fecha_llegada_soli.strftime('%Y-%m-%d') if ruta.fecha_llegada_soli else '',
                    'Hora de Llegada': ruta.hora_llegada_soli.strftime('%H:%M:%S') if ruta.hora_llegada_soli else ''
                })

            # Preparar la respuesta con los datos de la cuenta bancaria
            cuenta_bancaria_data = {
                'Banco': banco.nombre_banco if banco else '',
                'Tipo de Cuenta': cuenta_bancaria.tipo_cuenta if cuenta_bancaria else '',
                'Número de Cuenta': cuenta_bancaria.numero_cuenta if cuenta_bancaria else ''
            }

            return JsonResponse({'solicitud': solicitud_data, 'datos_personales': datos_personales, 'rutas': rutas_data, 'cuenta_bancaria': cuenta_bancaria_data}, status=200)

        except Solicitudes.DoesNotExist:
            return JsonResponse({'error': 'La solicitud no existe'}, status=404)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado correspondiente al usuario no existe'}, status=404)

        except Cargos.DoesNotExist:
            return JsonResponse({'error': 'El cargo asociado al empleado no existe'}, status=404)

        except Unidades.DoesNotExist:
            return JsonResponse({'error': 'La unidad asociada al cargo no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ActualizarSolicitudView(View):
    def put(self, request, id_solicitud, *args, **kwargs):
        try:
            data = json.loads(request.body)
            nuevo_estado = data.get('estado_solicitud')

            if nuevo_estado not in ['pendiente', 'aceptado', 'cancelado']:
                return JsonResponse({'error': 'Estado de solicitud no válido'}, status=400)

            try:
                solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)
                solicitud.estado_solicitud = nuevo_estado
                solicitud.save()

                return JsonResponse({'mensaje': f'Solicitud actualizada a {nuevo_estado} exitosamente'}, status=200)

            except Solicitudes.DoesNotExist:
                return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error al actualizar la solicitud: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EditarSolicitudView(View):
    def put(self, request, id_solicitud, *args, **kwargs):
        try:
            data = json.loads(request.body)
            solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)

            # Actualizar los campos de la solicitud
            solicitud.motivo_movilizacion = data.get('motivo_movilizacion', solicitud.motivo_movilizacion)
            solicitud.lugar_servicio = data.get('lugar_servicio', solicitud.lugar_servicio)
            solicitud.fecha_salida_solicitud = parse_date(data.get('fecha_salida_solicitud')) or solicitud.fecha_salida_solicitud
            solicitud.hora_salida_solicitud = parse_time(data.get('hora_salida_solicitud')) or solicitud.hora_salida_solicitud
            solicitud.fecha_llegada_solicitud = parse_date(data.get('fecha_llegada_solicitud')) or solicitud.fecha_llegada_solicitud
            solicitud.hora_llegada_solicitud = parse_time(data.get('hora_llegada_solicitud')) or solicitud.hora_llegada_solicitud
            solicitud.descripcion_actividades = data.get('descripcion_actividades', solicitud.descripcion_actividades)
            solicitud.listado_empleado = data.get('listado_empleado', solicitud.listado_empleado)

            with transaction.atomic():
                solicitud.save()

                # Actualizar o crear rutas de transporte
                rutas = data.get('rutas', [])
                TransporteSolicitudes.objects.filter(id_solicitud=solicitud).delete()
                for ruta in rutas:
                    TransporteSolicitudes.objects.create(
                        id_solicitud=solicitud,
                        tipo_transporte_soli=ruta.get('tipo_transporte_soli'),
                        nombre_transporte_soli=ruta.get('nombre_transporte_soli'),
                        ruta_soli=f"{ruta.get('ciudad_origen')} - {ruta.get('ciudad_destino')}",
                        fecha_salida_soli=parse_date(ruta.get('fecha_salida_soli')),
                        hora_salida_soli=parse_time(ruta.get('hora_salida_soli')),
                        fecha_llegada_soli=parse_date(ruta.get('fecha_llegada_soli')),
                        hora_llegada_soli=parse_time(ruta.get('hora_llegada_soli'))
                    )

                # Actualizar información de la cuenta bancaria
                banco_id = data.get('id_banco')
                tipo_cuenta = data.get('tipo_cuenta')
                numero_cuenta = data.get('numero_cuenta')

                if all([banco_id, tipo_cuenta, numero_cuenta]):
                    cuenta_bancaria = CuentasBancarias.objects.filter(id_solicitud=solicitud).first()
                    if cuenta_bancaria:
                        cuenta_bancaria.id_banco = Bancos.objects.get(id_banco=banco_id)
                        cuenta_bancaria.tipo_cuenta = tipo_cuenta
                        cuenta_bancaria.numero_cuenta = numero_cuenta
                        cuenta_bancaria.save()
                    else:
                        CuentasBancarias.objects.create(
                            id_banco=Bancos.objects.get(id_banco=banco_id),
                            id_empleado=solicitud.id_empleado,
                            id_solicitud=solicitud,
                            tipo_cuenta=tipo_cuenta,
                            numero_cuenta=numero_cuenta,
                            habilitado=1
                        )

            return JsonResponse({
                'mensaje': 'Solicitud actualizada exitosamente',
                'id_solicitud': solicitud.id_solicitud
            }, status=200)

        except Solicitudes.DoesNotExist:
            return JsonResponse({'error': 'La solicitud no existe'}, status=404)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Uno o más objetos relacionados no existen'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error al actualizar la solicitud: {str(e)}'}, status=500)
        
class ListarSolicitudesAceptadasSinInformeView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener las solicitudes del empleado con estado "aceptado" que no tienen un informe asociado
            solicitudes = Solicitudes.objects.filter(
                id_empleado=empleado,
                estado_solicitud='aceptado'
            ).exclude(
                informes__isnull=False
            )

            # Preparar la respuesta con los datos requeridos
            data = []
            for solicitud in solicitudes:
                codigo_solicitud = solicitud.generar_codigo_solicitud()
                data.append({
                    'id': solicitud.id_solicitud,
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

class ListarDatosInformeView(View):
    def get(self, request, id_solicitud, *args, **kwargs):
        try:
            # Obtener la solicitud por id
            solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)
            empleado = solicitud.id_empleado
            persona = empleado.id_persona
            cargo = empleado.id_cargo
            unidad = cargo.id_unidad

            # Combinar Distintivo, Apellidos y Nombres en una sola línea
            nombre_completo = f"{empleado.distintivo if empleado.distintivo else ''} {persona.apellidos if persona.apellidos else ''} {persona.nombres if persona.nombres else ''}".strip()

            # Formatear la fecha actual en el formato día-mes-año
            fecha_actual = timezone.now().strftime('%d-%m-%Y')

            # Preparar la respuesta con los datos requeridos
            data = {
                'Codigo de Solicitud': solicitud.generar_codigo_solicitud(),
                'Fecha Actual': fecha_actual,
                'Nombre Completo': nombre_completo,
                'Cargo': cargo.cargo if cargo.cargo else '',
                'Lugar de Servicio': solicitud.lugar_servicio if solicitud.lugar_servicio else '',
                'Nombre de Unidad': unidad.nombre_unidad if unidad.nombre_unidad else '',
                'Listado de Empleados': solicitud.listado_empleado if solicitud.listado_empleado else '',
            }

            return JsonResponse({'informe': data}, status=200)

        except Solicitudes.DoesNotExist:
            return JsonResponse({'error': 'La solicitud no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CrearInformeView(View):
    def post(self, request, id_solicitud, *args, **kwargs):
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)

            # Obtener la fecha y hora actual del sistema
            fecha_informe = date.today()
            hora_informe = datetime.now().time()

            # Validar y parsear las fechas y horas recibidas
            required_fields = ['fecha_salida_informe', 'hora_salida_informe', 'fecha_llegada_informe', 'hora_llegada_informe']
            fechas_horas = {field: parse_date(data.get(field)) if 'fecha' in field else parse_time(data.get(field)) for field in required_fields}
            print("Fechas y horas parseadas:", fechas_horas)

            if not all(fechas_horas.values()):
                return JsonResponse({'error': 'Fechas y horas del informe son requeridas y deben ser válidas'}, status=400)

            # Obtener los datos restantes
            observacion = data.get('observacion', '')

            # Crear el informe y los datos relacionados dentro de una transacción atómica
            with transaction.atomic():
                # Verificar que la solicitud exista
                solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)

                # Crear el informe con la fecha y hora actual y estado 0
                informe = Informes.objects.create(
                    id_solicitud=solicitud,
                    fecha_informe=fecha_informe,
                    fecha_salida_informe=fechas_horas['fecha_salida_informe'],
                    hora_salida_informe=fechas_horas['hora_salida_informe'],
                    fecha_llegada_informe=fechas_horas['fecha_llegada_informe'],
                    hora_llegada_informe=fechas_horas['hora_llegada_informe'],
                    observacion=observacion,
                    estado=0  # Asignar el estado como 0
                )

                # Crear los registros de transporte asociados al informe
                transportes = data.get('transportes', [])
                for transporte in transportes:
                    fechas_horas_transporte = {
                        'fecha_salida_info': parse_date(transporte.get('fecha_salida_info')),
                        'hora_salida_info': parse_time(transporte.get('hora_salida_info')),
                        'fecha_llegada_info': parse_date(transporte.get('fecha_llegada_info')),
                        'hora_llegada_info': parse_time(transporte.get('hora_llegada_info'))
                    }

                    if not all(fechas_horas_transporte.values()):
                        raise ValueError('Fechas y horas de transporte inválidas')

                    TransporteInforme.objects.create(
                        id_informe=informe,
                        tipo_transporte_info=transporte.get('tipo_transporte_info'),
                        nombre_transporte_info=transporte.get('nombre_transporte_info'),
                        ruta_info=transporte.get('ruta_info'),
                        fecha_salida_info=fechas_horas_transporte['fecha_salida_info'],
                        hora_salida_info=fechas_horas_transporte['hora_salida_info'],
                        fecha_llegada_info=fechas_horas_transporte['fecha_llegada_info'],
                        hora_llegada_info=fechas_horas_transporte['hora_llegada_info']
                    )

                # Crear los productos alcanzados asociados al informe
                productos = data.get('productos', [])
                for producto in productos:
                    ProductosAlcanzadosInformes.objects.create(
                        id_informe=informe,
                        descripcion=producto.get('descripcion', '')
                    )

            return JsonResponse({
                'mensaje': 'Informe creado exitosamente',
                'id_informe': informe.id_informes
            }, status=201)

        except Solicitudes.DoesNotExist:
            return JsonResponse({'error': 'La solicitud especificada no existe'}, status=404)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error al crear el informe: {str(e)}'}, status=500)
 
class ListarInformesView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener los informes asociados a las solicitudes del empleado
            informes = Informes.objects.filter(id_solicitud__id_empleado=empleado)

            # Preparar la respuesta con los datos requeridos
            data = []
            for informe in informes:
                codigo_solicitud = informe.id_solicitud.generar_codigo_solicitud()  # Asumiendo que el método existe en Solicitudes
                data.append({
                    'id_informes': informe.id_informes,
                    'codigo_solicitud': codigo_solicitud,
                    'fecha_informe': informe.fecha_informe.strftime('%Y-%m-%d') if informe.fecha_informe else '',
                    'estado':informe.estado,
                })

            return JsonResponse({'informes': data}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class DetalleInformeView(View):
    def get(self, request, id_informes, *args, **kwargs):
        try:
            # Obtener el informe por id
            informe = Informes.objects.get(id_informes=id_informes)
            solicitud = informe.id_solicitud
            empleado = solicitud.id_empleado
            persona = empleado.id_persona
            cargo = empleado.id_cargo
            unidad = cargo.id_unidad

            # Combinar Distintivo, Apellidos y Nombres en una sola línea
            nombre_completo = f"{empleado.distintivo if empleado.distintivo else ''} {persona.apellidos if persona.apellidos else ''} {persona.nombres if persona.nombres else ''}".strip()

            # Formatear la fecha del informe en el formato día-mes-año
            fecha_informe = informe.fecha_informe.strftime('%d-%m-%Y')

            # Obtener transportes asociados al informe
            transportes = TransporteInforme.objects.filter(id_informe=informe).values(
                'tipo_transporte_info',
                'nombre_transporte_info',
                'ruta_info',
                'fecha_salida_info',
                'hora_salida_info',
                'fecha_llegada_info',
                'hora_llegada_info'
            )

            transportes_list = []
            for transporte in transportes:
                transportes_list.append({
                    'Tipo de Transporte': transporte['tipo_transporte_info'],
                    'Nombre del Transporte': transporte['nombre_transporte_info'],
                    'Ruta': transporte['ruta_info'],
                    'Fecha de Salida': transporte['fecha_salida_info'].strftime('%d-%m-%Y') if transporte['fecha_salida_info'] else '',
                    'Hora de Salida': transporte['hora_salida_info'].strftime('%H:%M') if transporte['hora_salida_info'] else '',
                    'Fecha de Llegada': transporte['fecha_llegada_info'].strftime('%d-%m-%Y') if transporte['fecha_llegada_info'] else '',
                    'Hora de Llegada': transporte['hora_llegada_info'].strftime('%H:%M') if transporte['hora_llegada_info'] else '',
                })

            # Obtener productos alcanzados asociados al informe
            productos = ProductosAlcanzadosInformes.objects.filter(id_informe=informe).values('descripcion')

            productos_list = [producto['descripcion'] for producto in productos]

            # Preparar la respuesta con todos los detalles del informe
            data = {
                'Codigo de Solicitud': solicitud.generar_codigo_solicitud(),
                'Fecha del Informe': fecha_informe,
                'Nombre Completo': nombre_completo,
                'Cargo': cargo.cargo if cargo.cargo else '',
                'Lugar de Servicio': solicitud.lugar_servicio if solicitud.lugar_servicio else '',
                'Nombre de Unidad': unidad.nombre_unidad if unidad.nombre_unidad else '',
                'Listado de Empleados': solicitud.listado_empleado if solicitud.listado_empleado else '',
                'Fecha Salida Informe': informe.fecha_salida_informe.strftime('%d-%m-%Y') if informe.fecha_salida_informe else '',
                'Hora Salida Informe': informe.hora_salida_informe.strftime('%H:%M') if informe.hora_salida_informe else '',
                'Fecha Llegada Informe': informe.fecha_llegada_informe.strftime('%d-%m-%Y') if informe.fecha_llegada_informe else '',
                'Hora Llegada Informe': informe.hora_llegada_informe.strftime('%H:%M') if informe.hora_llegada_informe else '',
                'Observacion': informe.observacion if informe.observacion else '',
                'Transportes': transportes_list,
                'Productos Alcanzados': productos_list,
            }

            return JsonResponse({'detalle_informe': data}, status=200)

        except Informes.DoesNotExist:
            return JsonResponse({'error': 'El informe no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EditarInformeView(View):
    def post(self, request, id_informes, *args, **kwargs):
        try:
            informe = Informes.objects.get(id_informes=id_informes)
            data = json.loads(request.body.decode('utf-8'))

            print(f"Received data: {data}")  # Log received data

            def parse_date(date_string):
                try:
                    return parser.parse(date_string).date()
                except ValueError:
                    raise ValueError(f"Invalid date format: {date_string}")

            def parse_time(time_string):
                try:
                    return datetime.strptime(time_string, '%H:%M').time()
                except ValueError:
                    raise ValueError(f"Invalid time format: {time_string}")

            with transaction.atomic():
                # Actualizar campos básicos del informe
                informe.fecha_salida_informe = parse_date(data['fecha_salida_informe'])
                informe.hora_salida_informe = parse_time(data['hora_salida_informe'])
                informe.fecha_llegada_informe = parse_date(data['fecha_llegada_informe'])
                informe.hora_llegada_informe = parse_time(data['hora_llegada_informe'])
                informe.observacion = data.get('observacion', informe.observacion)
                informe.estado=1
                informe.save()

                # Actualizar transportes
                TransporteInforme.objects.filter(id_informe=informe).delete()
                for transporte in data.get('transportes', []):
                    TransporteInforme.objects.create(
                        id_informe=informe,
                        tipo_transporte_info=transporte['tipo_transporte_info'],
                        nombre_transporte_info=transporte['nombre_transporte_info'],
                        ruta_info=transporte['ruta_info'],
                        fecha_salida_info=parse_date(transporte['fecha_salida_info']),
                        hora_salida_info=parse_time(transporte['hora_salida_info']),
                        fecha_llegada_info=parse_date(transporte['fecha_llegada_info']),
                        hora_llegada_info=parse_time(transporte['hora_llegada_info'])
                    )

                # Actualizar productos alcanzados
                ProductosAlcanzadosInformes.objects.filter(id_informe=informe).delete()
                for producto in data.get('productos', []):
                    ProductosAlcanzadosInformes.objects.create(
                        id_informe=informe,
                        descripcion=producto['descripcion']
                    )

            return JsonResponse({
                'mensaje': 'Informe actualizado exitosamente',
                'id_informe': informe.id_informes
            }, status=200)

        except Informes.DoesNotExist:
            return JsonResponse({'error': 'El informe especificado no existe'}, status=404)
        except KeyError as e:
            print(f"KeyError: {str(e)}")
            print(f"Received data: {data}")
            return JsonResponse({'error': f'Falta el campo requerido: {str(e)}'}, status=400)
        except ValueError as e:
            print(f"ValueError: {str(e)}")
            print(f"Received data: {data}")
            return JsonResponse({'error': f'Error de formato: {str(e)}'}, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(f"Received data: {data}")
            return JsonResponse({'error': f'Error al actualizar el informe: {str(e)}'}, status=500)
        

class ListarInformesSinFacturasView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Obtener el usuario y el empleado asociado
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)

            # Obtener las solicitudes del empleado con motivo de movilización específico
            solicitudes = Solicitudes.objects.filter(
                id_empleado=empleado,
                motivo_movilizacion__in=['MOVILIZACIONES', 'VIÁTICOS']
            )

            # Obtener los informes asociados a las solicitudes filtradas y que no tienen facturas asociadas
            informes = Informes.objects.filter(
                id_solicitud__in=solicitudes
            ).exclude(
                id_informes__in=FacturasInformes.objects.values_list('id_informe', flat=True)
            ).filter(
                estado=1  # Filtrar por estado "completo"
            )

            # Preparar la respuesta con los datos requeridos
            data = []
            for informe in informes:
                codigo_solicitud = informe.id_solicitud.generar_codigo_solicitud()
                data.append({
                    'id_informes': informe.id_informes,
                    'Codigo de Solicitud': codigo_solicitud,
                    'Fecha Solicitud': informe.id_solicitud.fecha_solicitud.strftime('%Y-%m-%d') if informe.id_solicitud.fecha_solicitud else '',
                })

            return JsonResponse({'informes': data}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado correspondiente al usuario no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CrearJustificacionView(View):
    def post(self, request, id_informe, *args, **kwargs):
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)

            facturas = data.get('facturas', [])

            if not facturas:
                return JsonResponse({'error': 'Debe proporcionar al menos una factura.'}, status=400)

            with transaction.atomic():
                informe = Informes.objects.get(id_informes=id_informe)

                justificaciones_creadas = []
                total_factura = 0.0  # Inicializar como float

                for factura in facturas:
                    tipo_documento = factura.get('tipo_documento')
                    numero_factura = factura.get('numero_factura')
                    fecha_emision_str = factura.get('fecha_emision')
                    detalle_documento = factura.get('detalle_documento', '')
                    valor = factura.get('valor')

                    if not all([tipo_documento, numero_factura, fecha_emision_str, valor is not None]):
                        raise ValidationError('Todos los campos requeridos deben ser proporcionados para cada factura')

                    try:
                        fecha_emision = datetime.strptime(fecha_emision_str, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError('Formato de fecha inválido. Use YYYY-MM-DD.')

                    try:
                        valor = float(valor)
                    except ValueError:
                        raise ValidationError('El valor debe ser un número válido.')

                    justificacion = FacturasInformes.objects.create(
                        id_informe=informe,
                        tipo_documento=tipo_documento,
                        numero_factura=numero_factura,
                        fecha_emision=fecha_emision,
                        detalle_documento=detalle_documento,
                        valor=valor
                    )

                    # Crear registro en la tabla EstadoFactura
                    EstadoFactura.objects.create(
                        id_factura=justificacion,
                        estado=0  # Estado inicial como 'incompleto'
                    )

                    justificaciones_creadas.append(justificacion.id_factura)
                    total_factura += valor

                total_factura_record, created = TotalFactura.objects.get_or_create(
                    id_factura__id_informe=informe,
                    defaults={'id_factura': justificacion, 'total': total_factura}
                )

                if not created:
                    total_factura_record.total = total_factura
                    total_factura_record.save()

            return JsonResponse({
                'mensaje': 'Justificaciones creadas exitosamente',
                'justificaciones': justificaciones_creadas
            }, status=201)

        except Informes.DoesNotExist:
            return JsonResponse({'error': 'El informe especificado no existe'}, status=404)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error al crear las justificaciones: {str(e)}'}, status=500)

class ListarFacturaInformesView(View):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)
            
            informes = Informes.objects.filter(id_solicitud__id_empleado=empleado)
            print(f"Informes encontrados: {informes}")  # Debugging
             
            data = []
            for informe in informes:
                facturas = FacturasInformes.objects.filter(id_informe=informe)
                print(f"Facturas encontradas para el informe {informe.id_informes}: {facturas}")  # Debugging
                
                estado_facturas = EstadoFactura.objects.filter(id_factura__in=facturas).values_list('estado', flat=True)
                estado_factura = estado_facturas[0] if estado_facturas else 0
                
                codigo_solicitud = informe.id_solicitud.generar_codigo_solicitud()
                data.append({
                    'id_informe': informe.id_informes,
                    'codigo_solicitud': codigo_solicitud,
                    'fecha_informe': informe.fecha_informe.strftime('%Y-%m-%d') if informe.fecha_informe else '',
                    'estado_factura': estado_factura
                })

            return JsonResponse({'informes': data}, status=200)

        except Usuarios.DoesNotExist:
            return JsonResponse({'error': 'El usuario no existe'}, status=404)

        except Empleados.DoesNotExist:
            return JsonResponse({'error': 'El empleado no existe'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EditarJustificacionView(View):
    def post(self, request, id_informe, *args, **kwargs):
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)

            facturas = data.get('facturas', [])
            if not facturas:
                return JsonResponse({'error': 'Debe proporcionar al menos una factura.'}, status=400)

            justificaciones_actualizadas = []
            ids_facturas_existentes = set()

            with transaction.atomic():
                informe = Informes.objects.get(id_informes=id_informe)
                
                # Obtener todas las facturas actuales asociadas al informe
                facturas_existentes = FacturasInformes.objects.filter(id_informe=informe)

                total_factura = 0.0  # Inicializar el total como float

                for factura in facturas:
                    tipo_documento = factura.get('tipo_documento')
                    numero_factura = factura.get('numero_factura')
                    fecha_emision_str = factura.get('fecha_emision')
                    detalle_documento = factura.get('detalle_documento', '')
                    valor = factura.get('valor')

                    if not all([tipo_documento, numero_factura, fecha_emision_str, valor is not None]):
                        raise ValidationError('Todos los campos requeridos deben ser proporcionados para cada factura.')

                    try:
                        fecha_emision = datetime.strptime(fecha_emision_str, '%d-%m-%Y').date()
                    except ValueError:
                        raise ValidationError('Formato de fecha inválido. Use DD-MM-YYYY.')

                    try:
                        valor = float(valor)
                    except ValueError:
                        raise ValidationError('El valor debe ser un número válido.')

                    # Intentar encontrar una factura existente con el mismo número
                    justificacion = facturas_existentes.filter(numero_factura=numero_factura).first()

                    if justificacion:
                        # Si la factura existe, actualizarla
                        justificacion.tipo_documento = tipo_documento
                        justificacion.fecha_emision = fecha_emision
                        justificacion.detalle_documento = detalle_documento
                        justificacion.valor = valor
                        justificacion.save()

                        # Actualizar o crear el estado de la factura en la tabla EstadoFactura
                        estado_factura, created = EstadoFactura.objects.get_or_create(
                            id_factura=justificacion,
                            defaults={'estado': 1}  # Asumir que la factura editada está 'completa'
                        )
                        if not created:
                            estado_factura.estado = 1  # Actualizar el estado si ya existía
                            estado_factura.save()

                        # Añadir el id de la factura existente
                        ids_facturas_existentes.add(justificacion.id_factura)
                    else:
                        # Si la factura no existe, crear una nueva
                        justificacion = FacturasInformes.objects.create(
                            id_informe=informe,
                            tipo_documento=tipo_documento,
                            numero_factura=numero_factura,
                            fecha_emision=fecha_emision,
                            detalle_documento=detalle_documento,
                            valor=valor
                        )

                        # Crear un nuevo registro en EstadoFactura para la nueva factura
                        EstadoFactura.objects.create(
                            id_factura=justificacion,
                            estado=1  # Estado inicial como 'completo'
                        )

                        # Añadir el id de la nueva factura
                        ids_facturas_existentes.add(justificacion.id_factura)

                    justificaciones_actualizadas.append(justificacion.id_factura)
                    total_factura += valor

                # Actualizar o crear el total de la factura
                total_factura_record, created = TotalFactura.objects.get_or_create(
                    id_factura__id_informe=informe,
                    defaults={'total': total_factura}
                )

                if not created:
                    total_factura_record.total = total_factura
                    total_factura_record.save()

                # Eliminar facturas que ya no están en la solicitud
                facturas_existentes.exclude(id_factura__in=ids_facturas_existentes).delete()

            return JsonResponse({
                'mensaje': 'Justificaciones actualizadas exitosamente',
                'justificaciones': justificaciones_actualizadas
            }, status=200)

        except Informes.DoesNotExist:
            return JsonResponse({'error': 'El informe especificado no existe.'}, status=404)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error al actualizar las justificaciones: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ListarDetalleFacturasView(View):
    def get(self, request, id_usuario, id_informe, *args, **kwargs):
        try:
            # Obtener el token del encabezado de la solicitud
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            # Decodificar el token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            # Verificar que el ID de usuario en el token coincida con el ID de usuario en la URL
            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)

            # Obtener las facturas asociadas al informe
            facturas = FacturasInformes.objects.filter(id_informe=id_informe).values(
                'id_factura',
                'tipo_documento',
                'numero_factura',
                'fecha_emision',
                'detalle_documento',
                'valor'
            )

            if not facturas:
                return JsonResponse({'error': 'No se encontraron facturas para el informe especificado.'}, status=404)

            # Crear una lista con los detalles de las facturas
            facturas_list = []
            for factura in facturas:
                factura_data = {
                    'id_factura': factura['id_factura'],
                    'tipo_documento': factura['tipo_documento'],
                    'numero_factura': factura['numero_factura'],
                    'fecha_emision': factura['fecha_emision'].strftime('%d-%m-%Y'),
                    'detalle_documento': factura['detalle_documento'],
                    'valor': str(factura['valor']) if factura['valor'] is not None else '0.00'
                }
                facturas_list.append(factura_data)

            return JsonResponse({
                'mensaje': 'Facturas listadas exitosamente',
                'facturas': facturas_list
            }, status=200, safe=False)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Exception as e:
            print(f"Error al listar las facturas: {str(e)}")  # Log de error para depuración
            return JsonResponse({'error': f'Error al listar las facturas: {str(e)}'}, status=500)
       

@method_decorator(csrf_exempt, name='dispatch')
class ListarDetalleJustificacionesView(View):
    def get(self, request, id_informe, *args, **kwargs):
        try:
            print(f"ID Informe recibido: {id_informe}")

            # Diccionario para convertir nombres de meses en inglés a español
            meses_espanol = {
                'January': 'enero', 'February': 'febrero', 'March': 'marzo',
                'April': 'abril', 'May': 'mayo', 'June': 'junio',
                'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
                'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
            }

            # Obtener el informe
            informe = Informes.objects.get(pk=id_informe)

            # Obtener la solicitud asociada y generar el código
            solicitud = informe.id_solicitud
            codigo_solicitud = solicitud.generar_codigo_solicitud()

            # Formatear las fechas de salida y llegada
            fecha_salida = informe.fecha_salida_informe
            fecha_llegada = informe.fecha_llegada_informe

            if fecha_salida and fecha_llegada:
                mes_salida = fecha_salida.strftime('%B')
                mes_llegada = fecha_llegada.strftime('%B')
                
                mes_salida_es = meses_espanol.get(mes_salida, mes_salida)
                mes_llegada_es = meses_espanol.get(mes_llegada, mes_llegada)

                if fecha_salida.month == fecha_llegada.month:
                    rango_fechas = f"del {fecha_salida.day} al {fecha_llegada.day} de {mes_salida_es} del {fecha_salida.year}"
                else:
                    rango_fechas = f"del {fecha_salida.day} de {mes_salida_es} al {fecha_llegada.day} de {mes_llegada_es} del {fecha_llegada.year}"
            else:
                rango_fechas = 'Fechas no disponibles'

            # Obtener el empleado asociado a la solicitud
            empleado = solicitud.id_empleado
            persona = empleado.id_persona

            # Obtener el cargo del empleado
            cargo_obj = Cargos.objects.get(id_cargo=empleado.id_cargo.id_cargo)  # Asegúrate que `id_cargo` esté relacionado con empleado
            nombre_cargo = cargo_obj.cargo

            # Preparar los datos del empleado
            distintivo = empleado.distintivo or ''
            nombres = persona.nombres or ''
            apellidos = persona.apellidos or ''
            numero_cedula = persona.numero_cedula or ''

            # Formato para el campo deseado
            nombre_completo = f"{distintivo} {nombres} {apellidos}"
            cedula = f"CI. {numero_cedula}"

            # Obtener las facturas asociadas
            facturas = FacturasInformes.objects.filter(id_informe=id_informe).values(
                'id_factura',
                'tipo_documento',
                'numero_factura',
                'fecha_emision',
                'detalle_documento',
                'valor'
            )

            if not facturas:
                return JsonResponse({'error': 'No se encontraron facturas para el informe especificado.'}, status=404)

            # Preparar la lista de facturas
            facturas_list = []
            for factura in facturas:
                valor_factura = float(factura['valor']) if factura['valor'] is not None else 0.00
                factura_data = {
                    'id_factura': factura['id_factura'],
                    'tipo_documento': factura['tipo_documento'],
                    'numero_factura': factura['numero_factura'],
                    'fecha_emision': factura['fecha_emision'].strftime('%d-%m-%Y'),
                    'detalle_documento': factura['detalle_documento'],
                    'valor': valor_factura
                }
                facturas_list.append(factura_data)

            # Calcular el total asociado a las facturas
            total_factura = TotalFactura.objects.filter(id_factura__in=[factura['id_factura'] for factura in facturas]).aggregate(total_sum=Sum('total'))['total_sum'] or 0.00

            # Convertir total_factura a cadena para evitar errores de tipo
            total_factura_str = f"{total_factura:.2f}"

            return JsonResponse({
                'codigo_solicitud': codigo_solicitud,
                'rango_fechas': rango_fechas,
                'nombre_completo': nombre_completo,
                'cedula': cedula,
                'cargo': nombre_cargo,  # Añadir el cargo al JSON de respuesta
                'facturas': facturas_list,
                'total_factura': total_factura_str
            }, status=200, safe=False)

        except Informes.DoesNotExist:
            return JsonResponse({'error': 'Informe no encontrado.'}, status=404)

        except Exception as e:
            print(f"Error al listar el detalle de las justificaciones: {str(e)}")
            return JsonResponse({'error': f'Error al listar el detalle de las justificaciones: {str(e)}'}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class CrearMotivoCanceladoView(View):
    def post(self, request, id_solicitud, *args, **kwargs):
        try:
            data = json.loads(request.body)
            motivo_cancelado = data.get('motivo_cancelado')

            if not motivo_cancelado:
                return JsonResponse({'error': 'Debe proporcionar el motivo de cancelación.'}, status=400)

            with transaction.atomic():
                solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)

                # Crear el motivo cancelado
                motivo = MotivoCancelado.objects.create(
                    id_solicitud=solicitud,
                    motivo_cancelado=motivo_cancelado
                )

            return JsonResponse({
                'mensaje': 'Motivo de cancelación creado exitosamente',
                'id_motivo_cancelado': motivo.id_motivo_cancelado
            }, status=201)

        except Solicitudes.DoesNotExist:
            return JsonResponse({'error': 'La solicitud especificada no existe'}, status=404)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error al crear el motivo de cancelación: {str(e)}'}, status=500)
        

class ListarMotivosCanceladosView(View):
    def get(self, request, id_solicitud, *args, **kwargs):
        try:
            # Verificar que la solicitud exista
            solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)

            # Obtener los motivos de cancelación asociados a la solicitud
            motivos_cancelados = MotivoCancelado.objects.filter(id_solicitud=solicitud)

            # Formatear la respuesta
            motivos_list = [{
                'id_motivo_cancelado': motivo.id_motivo_cancelado,
                'motivo_cancelado': motivo.motivo_cancelado
            } for motivo in motivos_cancelados]

            return JsonResponse({
                'solicitud': id_solicitud,
                'motivos_cancelados': motivos_list
            }, status=200)

        except Solicitudes.DoesNotExist:
            return JsonResponse({'error': 'La solicitud especificada no existe'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error al obtener los motivos de cancelación: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GenerarPdfInformeView(View):
    def get(self, request, id_usuario, id_informe):
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

            informe = Informes.objects.get(id_informes=id_informe)
            if not informe:
                return JsonResponse({"error": "Informe no encontrado"}, status=404)

            include_header_footer = request.GET.get('include_header_footer', 'true').lower() == 'true'
            return generar_pdf_informe(informe, include_header_footer)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except Informes.DoesNotExist:
            return JsonResponse({"error": "Orden de movilización no encontrada"}, status=404)

        except Exception as e:
            print(f'Error al generar el PDF: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

from weasyprint import HTML, CSS
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
import logging

def generar_pdf_informe(informe, include_header_footer):
    try:
        template_path = 'informe_viaje_pdf.html'

        solicitud = informe.id_solicitud
        empleado = solicitud.id_empleado
        persona = empleado.id_persona
        cargo = empleado.id_cargo
        unidad = cargo.id_unidad

        nombre_completo = f"{empleado.distintivo if empleado.distintivo else ''} {persona.apellidos if persona.apellidos else ''} {persona.nombres if persona.nombres else ''}".strip()
        fecha_informe = informe.fecha_informe.strftime('%d-%m-%Y')

        # Obtener el jefe de la unidad
        jefe_unidad = Empleados.objects.filter(id_cargo__id_unidad=unidad.id_unidad, es_jefe=True).first()
        nombre_jefe_unidad = f"{jefe_unidad.distintivo} {jefe_unidad.id_persona.apellidos} {jefe_unidad.id_persona.nombres}" if jefe_unidad else 'No asignado'
        cedula_jefe_unidad = jefe_unidad.id_persona.numero_cedula if jefe_unidad else 'No asignado'

        # Obtener el jefe de estación
        jefe_estacion = Empleados.objects.filter(id_cargo__id_unidad__id_estacion=unidad.id_estacion, es_director=True).first()
        nombre_jefe_estacion = f"{jefe_estacion.distintivo} {jefe_estacion.id_persona.apellidos} {jefe_estacion.id_persona.nombres}" if jefe_estacion else 'No asignado'
        cedula_jefe_estacion = jefe_estacion.id_persona.numero_cedula if jefe_estacion else 'No asignado'
        nombre_estacion = unidad.id_estacion.nombre_estacion if unidad.id_estacion else 'No asignada'

        transportes = TransporteInforme.objects.filter(id_informe=informe).values(
            'tipo_transporte_info',
            'nombre_transporte_info',
            'ruta_info',
            'fecha_salida_info',
            'hora_salida_info',
            'fecha_llegada_info',
            'hora_llegada_info'
        )

        transportes_list = []
        for transporte in transportes:
            transportes_list.append({
                'Tipo_de_Transporte': transporte['tipo_transporte_info'],
                'Nombre_del_Transporte': transporte['nombre_transporte_info'],
                'Ruta': transporte['ruta_info'],
                'Fecha_de_Salida': transporte['fecha_salida_info'].strftime('%d-%m-%Y') if transporte['fecha_salida_info'] else '',
                'Hora_de_Salida': transporte['hora_salida_info'].strftime('%H:%M') if transporte['hora_salida_info'] else '',
                'Fecha_de_Llegada': transporte['fecha_llegada_info'].strftime('%d-%m-%Y') if transporte['fecha_llegada_info'] else '',
                'Hora_de_Llegada': transporte['hora_llegada_info'].strftime('%H:%M') if transporte['hora_llegada_info'] else '',
            })

        productos = ProductosAlcanzadosInformes.objects.filter(id_informe=informe).values('descripcion')
        productos_list = [producto['descripcion'] for producto in productos]
        productos_alcanzados = ''.join(productos_list)

        encabezados = Encabezados.objects.first()  # Suponiendo que solo hay un encabezado
        
        context = {
            'codigo_solicitud': solicitud.generar_codigo_solicitud(),
            'fecha_informe': fecha_informe,
            'nombre_completo': nombre_completo,
            'cargo': cargo.cargo if cargo.cargo else '',
            'cedula': persona.numero_cedula if persona.numero_cedula else '',
            'lugar_servicio': solicitud.lugar_servicio if solicitud.lugar_servicio else '',
            'nombre_unidad': unidad.nombre_unidad if unidad.nombre_unidad else '',
            'listado_empleados': solicitud.listado_empleado if solicitud.listado_empleado else '',
            'fecha_salida_informe': informe.fecha_salida_informe.strftime('%d-%m-%Y') if informe.fecha_salida_informe else '',
            'hora_salida_informe': informe.hora_salida_informe.strftime('%H:%M') if informe.hora_salida_informe else '',
            'fecha_llegada_informe': informe.fecha_llegada_informe.strftime('%d-%m-%Y') if informe.fecha_llegada_informe else '',
            'hora_llegada_informe': informe.hora_llegada_informe.strftime('%H:%M') if informe.hora_llegada_informe else '',
            'observacion': informe.observacion if informe.observacion else '',
            'transportes': transportes_list,
            'productos_alcanzados': productos_alcanzados,
            'nombre_jefe_unidad': nombre_jefe_unidad,
            'cedula_jefe_unidad': cedula_jefe_unidad,
            'nombre_jefe_estacion': nombre_jefe_estacion,
            'cedula_jefe_estacion': cedula_jefe_estacion,
            'nombre_estacion': nombre_estacion,
            'encabezado_superior': encabezados.encabezado_superior if encabezados and include_header_footer else '',
            'encabezado_inferior': encabezados.encabezado_inferior if encabezados and include_header_footer else '',
        }

        html_content = render_to_string(template_path, context)

        pdf_file = BytesIO()
        if include_header_footer:
            HTML(string=html_content).write_pdf(pdf_file, stylesheets=[CSS(string='''@page { size: A4; margin: 2cm; @top-center { content: element(header); } @bottom-center { content: element(footer); }} #header { position: running(header); width: 100%; text-align: center; font-size: 10px; } #footer { position: running(footer); width: 100%; text-align: center; font-size: 10px; } ''')])
        else:
            HTML(string=html_content).write_pdf(pdf_file)

        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="informe_{informe.id_informes}.pdf"'

        return response

    except Exception as e:
        logger.error(f'Error en generar_pdf: {str(e)}')
        return HttpResponse(f'Error al generar el PDF: {str(e)}', status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GenerarPdfFacturasView(View):
    def get(self, request, id_usuario, id_informe):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            token_id_usuario = payload.get('id_usuario')
            if not token_id_usuario:
                raise AuthenticationFailed('ID de usuario no encontrado en el token')

            if int(token_id_usuario) != id_usuario:
                return JsonResponse({'error': 'ID de usuario en el token no coincide con el de la URL'}, status=403)


            facturas = FacturasInformes.objects.filter(id_informe=id_informe).values(
                'id_factura',
                'tipo_documento',
                'numero_factura',
                'fecha_emision',
                'detalle_documento',
                'valor'
            )

            if not facturas:
                return JsonResponse({'error': 'No se encontraron facturas para el informe especificado.'}, status=404)

            facturas_list = []
            for factura in facturas:
                factura_data = {
                    'id_factura': factura['id_factura'],
                    'tipo_documento': factura['tipo_documento'],
                    'numero_factura': factura['numero_factura'],
                    'fecha_emision': factura['fecha_emision'].strftime('%d-%m-%Y'),
                    'detalle_documento': factura['detalle_documento'],
                    'valor': str(factura['valor']) if factura['valor'] is not None else '0.00'
                }
                facturas_list.append(factura_data)

            include_header_footer = request.GET.get('includeHeaderFooter', 'true').lower() == 'true'
            return generar_pdf_facturas(facturas_list, id_informe, include_header_footer)

        except Exception as e:
            print(f"Error al generar el PDF: {str(e)}")  
            return JsonResponse({'error': f'Error al generar el PDF: {str(e)}'}, status=500)

def generar_pdf_facturas(facturas_list, id_informe, include_header_footer):
    try:
        template_path = 'facturas_informe_pdf.html'
        
        # Obtener detalles del informe y del empleado
        informe = Informes.objects.get(id_informes=id_informe)
        solicitud = informe.id_solicitud
        empleado = solicitud.id_empleado
        persona = empleado.id_persona
        cedula = persona.numero_cedula
        cargo = empleado.id_cargo
        unidad = cargo.id_unidad

        fecha_salida = informe.fecha_salida_informe
        fecha_llegada = informe.fecha_llegada_informe

        meses_espanol = {
            'January': 'enero', 'February': 'febrero', 'March': 'marzo',
            'April': 'abril', 'May': 'mayo', 'June': 'junio',
            'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
            'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
        }

        if fecha_salida and fecha_llegada:
            mes_salida = fecha_salida.strftime('%B')
            mes_llegada = fecha_llegada.strftime('%B') 
            mes_salida_es = meses_espanol.get(mes_salida, mes_salida)
            mes_llegada_es = meses_espanol.get(mes_llegada, mes_llegada)
            if fecha_salida.month == fecha_llegada.month:
                rango_fechas = f"del {fecha_salida.day} al {fecha_llegada.day} de {mes_salida_es} del {fecha_salida.year}"
            else:
                rango_fechas = f"del {fecha_salida.day} de {mes_salida_es} al {fecha_llegada.day} de {mes_llegada_es} del {fecha_llegada.year}"
        else:
            rango_fechas = 'Fechas no disponibles'

        # Calcular el total de los valores de las facturas
        total_valor = sum(float(factura['valor']) for factura in facturas_list)

        # Formatear datos para el contexto
        nombre_completo = f"{empleado.distintivo if empleado.distintivo else ''} {persona.apellidos if persona.apellidos else ''} {persona.nombres if persona.nombres else ''}".strip()

        # Obtener encabezados
        encabezados = Encabezados.objects.first()  # Suponiendo que hay un único conjunto de encabezados
        
        # Crear el contexto para el template
        context = {
            'codigo_solicitud': solicitud.generar_codigo_solicitud(),
            'fecha_comision': rango_fechas,
            'nombre_completo': nombre_completo,
            'cedula': cedula,
            'cargo': cargo.cargo if cargo.cargo else '',
            'lugar_servicio': solicitud.lugar_servicio if solicitud.lugar_servicio else '',
            'nombre_unidad': unidad.nombre_unidad if unidad.nombre_unidad else '',
            'facturas': facturas_list,
            'total_valor': total_valor,
        }

        if include_header_footer:
            encabezados = Encabezados.objects.first()
            context.update({
                'encabezado_superior': encabezados.encabezado_superior if encabezados else '',
                'encabezado_inferior': encabezados.encabezado_inferior if encabezados else '',
        })

        # Renderizar el template a HTML
        html_content = render_to_string(template_path, context)

        # Crear el PDF usando WeasyPrint
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file, stylesheets=[CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
                @top-center {
                    content: element(header);
                }
                @bottom-center {
                    content: element(footer);
                }
            }
            #header {
                position: running(header);
                width: 100%;
                text-align: center;
                font-size: 10px;
                border-bottom: 1px solid black;
            }
            #footer {
                position: running(footer);
                width: 100%;
                text-align: center;
                font-size: 10px;
                border-top: 1px solid black;
            }
        ''')])

        # Configurar la respuesta HTTP
        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="facturas_{informe.id_informes}.pdf"'

        return response

    except Exception as e:
        logger.error(f'Error en generar_pdf_facturas: {str(e)}')
        return HttpResponse(f'Error al generar el PDF: {str(e)}', status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GenerarPdfSolicitudView(View):
    def get(self, request, id_usuario, id_solicitud):
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

            solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)
            if not solicitud:
                return JsonResponse({"error": "Solicitud no encontrada"}, status=404)

            include_header_footer = request.GET.get('include_header_footer', 'true').lower() == 'true'
            return generar_pdf_solicitud(solicitud, include_header_footer)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        except AuthenticationFailed as e:
            return JsonResponse({'error': str(e)}, status=403)

        except Solicitudes.DoesNotExist:
            return JsonResponse({"error": "Solicitud no encontrada"}, status=404)

        except Exception as e:
            logger.error(f'Error al generar el PDF: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)


def generar_pdf_solicitud(solicitud, include_header_footer):
    try:
        template_path = 'solicitud_viaje_pdf.html'

        empleado = solicitud.id_empleado
        persona = empleado.id_persona
        cargo = empleado.id_cargo
        unidad = cargo.id_unidad

        nombre_completo = f"{empleado.distintivo if empleado.distintivo else ''} {persona.apellidos if persona.apellidos else ''} {persona.nombres if persona.nombres else ''}".strip()
        fecha_solicitud = solicitud.fecha_solicitud.strftime('%d-%m-%Y')

        # Obtener el jefe de la unidad
        jefe_unidad = Empleados.objects.filter(id_cargo__id_unidad=unidad.id_unidad, es_jefe=True).first()
        nombre_jefe_unidad = f"{jefe_unidad.distintivo} {jefe_unidad.id_persona.apellidos} {jefe_unidad.id_persona.nombres}" if jefe_unidad else 'No asignado'
        cedula_jefe_unidad = jefe_unidad.id_persona.numero_cedula if jefe_unidad else 'No asignado'

        # Obtener el jefe de estación
        jefe_estacion = Empleados.objects.filter(id_cargo__id_unidad__id_estacion=unidad.id_estacion, es_director=True).first()
        nombre_jefe_estacion = f"{jefe_estacion.distintivo} {jefe_estacion.id_persona.apellidos} {jefe_estacion.id_persona.nombres}" if jefe_estacion else 'No asignado'
        cedula_jefe_estacion = jefe_estacion.id_persona.numero_cedula if jefe_estacion else 'No asignado'
        nombre_estacion = unidad.id_estacion.nombre_estacion if unidad.id_estacion else 'No asignada'

        encabezados = Encabezados.objects.first() if include_header_footer else None

        transportes = TransporteSolicitudes.objects.filter(id_solicitud=solicitud.id_solicitud)
        cuenta_bancaria = CuentasBancarias.objects.filter(id_solicitud=solicitud.id_solicitud).first()
        banco = cuenta_bancaria.id_banco.nombre_banco if cuenta_bancaria and cuenta_bancaria.id_banco else ''
        tipo_cuenta = cuenta_bancaria.tipo_cuenta if cuenta_bancaria else ''
        numero_cuenta = cuenta_bancaria.numero_cuenta if cuenta_bancaria else ''

        motivo = solicitud.motivo_movilizacion
        viaticos_checked = 'checked' if motivo == 'VIÁTICOS' else ''
        movilizaciones_checked = 'checked' if motivo == 'MOVILIZACIONES' else ''
        subsistencias_checked = 'checked' if motivo == 'SUBSISTENCIAS' else ''
        alimentacion_checked = 'checked' if motivo == 'ALIMENTACIÓN' else ''

        context = {
            'codigo_solicitud': solicitud.generar_codigo_solicitud(),
            'fecha_solicitud': fecha_solicitud,
            'nombre_completo': nombre_completo,
            'cargo': cargo.cargo if cargo.cargo else '',
            'cedula': persona.numero_cedula if persona.numero_cedula else '',
            'lugar_servicio': solicitud.lugar_servicio if solicitud.lugar_servicio else '',
            'descripcion_actividades': solicitud.descripcion_actividades if solicitud.descripcion_actividades else '',
            'nombre_unidad': unidad.nombre_unidad if unidad.nombre_unidad else '',
            'listado_empleados': solicitud.listado_empleado if solicitud.listado_empleado else '',
            'viaticos_checked': viaticos_checked,
            'movilizaciones_checked': movilizaciones_checked,
            'subsistencias_checked': subsistencias_checked,
            'alimentacion_checked': alimentacion_checked,
            'fecha_salida_solicitud': solicitud.fecha_salida_solicitud.strftime('%d-%m-%Y') if solicitud.fecha_salida_solicitud else '',
            'hora_salida_solicitud': solicitud.hora_salida_solicitud.strftime('%H:%M') if solicitud.hora_salida_solicitud else '',
            'fecha_llegada_solicitud': solicitud.fecha_llegada_solicitud.strftime('%d-%m-%Y') if solicitud.fecha_llegada_solicitud else '',
            'hora_llegada_solicitud': solicitud.hora_llegada_solicitud.strftime('%H:%M') if solicitud.hora_llegada_solicitud else '',
            'transportes': transportes,
            'banco': banco,
            'tipo_cuenta': tipo_cuenta,
            'numero_cuenta': numero_cuenta,
            'nombre_jefe_unidad': nombre_jefe_unidad,
            'cedula_jefe_unidad': cedula_jefe_unidad,
            'nombre_jefe_estacion': nombre_jefe_estacion,
            'cedula_jefe_estacion': cedula_jefe_estacion,
            'nombre_estacion': nombre_estacion,
        }

        if include_header_footer and encabezados:
            context.update({
                'encabezado_superior': encabezados.encabezado_superior,
                'encabezado_inferior': encabezados.encabezado_inferior
            })

        html_content = render_to_string(template_path, context)

        pdf_file = BytesIO()
        css_styles = '''
            @page {
                size: A4;
                margin: 2cm;
                {% if include_header_footer %}
                @top-center {
                    content: element(header);
                }
                @bottom-center {
                    content: element(footer);
                }
                {% endif %}
            }
            #header {
                {% if include_header_footer %}
                position: running(header);
                width: 100%;
                text-align: center;
                font-size: 10px;
                border-bottom: 1px solid black;
                {% endif %}
            }
            #footer {
                {% if include_header_footer %}
                position: running(footer);
                width: 100%;
                text-align: center;
                font-size: 10px;
                border-top: 1px solid black;
                {% endif %}
            }
        '''
        HTML(string=html_content).write_pdf(pdf_file, stylesheets=[CSS(string=css_styles)])

        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="solicitud_{solicitud.id_solicitud}.pdf"'

        return response

    except Exception as e:
        logger.error(f'Error en generar_pdf_solicitud: {str(e)}')
        return HttpResponse(f'Error al generar el PDF: {str(e)}', status=500)
