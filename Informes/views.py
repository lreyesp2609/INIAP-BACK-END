
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import jwt

from .models import Empleados, Personas, Unidades, Estaciones, Solicitudes, Informes, Usuarios,Bancos, Motivo,Provincias, Ciudades,Usuarios, Personas, Empleados, Cargos, Unidades, TransporteSolicitudes, Vehiculo, CuentasBancarias
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

from django.db import transaction

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
            # Obtener todos los bancos
            bancos = Bancos.objects.all()

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
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todas las solicitudes con estado pendiente
            solicitudes = Solicitudes.objects.filter(estado_solicitud='pendiente')

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

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ListarSolicitudesCanceladasAdminView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todas las solicitudes con estado pendiente
            solicitudes = Solicitudes.objects.filter(estado_solicitud='cancelado')

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

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

@method_decorator(csrf_exempt, name='dispatch')
class ListarSolicitudesAceptadasAdminView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todas las solicitudes con estado pendiente
            solicitudes = Solicitudes.objects.filter(estado_solicitud='aceptado')

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

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
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