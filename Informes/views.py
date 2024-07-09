
from django.shortcuts import render
from django.http import JsonResponse

from .models import Empleados, Personas, Unidades, Estaciones, Solicitudes, Informes, Usuarios
from datetime import datetime
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



def generar_numero_solicitud(request, id_solicitud):
    try:
        # Buscar la solicitud por ID
        solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)
        empleado = solicitud.id_empleado
        persona = Personas.objects.get(id_persona=empleado.id_persona.id_persona)

        # Obtener el informe asociado con la solicitud
        informe = Informes.objects.get(id_solicitud=id_solicitud)

        # Obtener la información de la persona y unidad
        nombres = persona.nombres.split()  # Asumiendo que los nombres están separados por espacio
        apellidos = persona.apellidos.split()  # Asumiendo que los apellidos están separados por espacio
        unidad = Unidades.objects.get(id_unidad=empleado.id_cargo.id_unidad.id_unidad)
        estacion = Estaciones.objects.get(id_estacion=unidad.id_estacion.id_estacion)

        # Generar el número de solicitud
        secuencia_informe = informe.secuencia_informe
        siglas_nombres = nombres[0][:1].upper() + (nombres[1][:1].upper() if len(nombres) >= 2 else '')
        siglas_apellidos = apellidos[0][:1].upper() + (apellidos[1][:1].upper() if len(apellidos) >= 2 else '')
        siglas_unidad = unidad.siglas_unidad
        siglas_estacion = estacion.siglas_estacion
        año_solicitud = datetime.now().year

        numero_solicitud = f"{secuencia_informe:03d}-{siglas_nombres}{siglas_apellidos}-{siglas_unidad}-INIAP-{siglas_estacion}-{año_solicitud}"

        return JsonResponse({"numero_solicitud": numero_solicitud})
    except Solicitudes.DoesNotExist:
        return JsonResponse({"error": "Solicitud no encontrada"}, status=404)
    except Empleados.DoesNotExist:
        return JsonResponse({"error": "Empleado no encontrado"}, status=404)
    except Personas.DoesNotExist:
        return JsonResponse({"error": "Persona no encontrada"}, status=404)
    except Informes.DoesNotExist:
        return JsonResponse({"error": "Informe no encontrado"}, status=404)
    except Unidades.DoesNotExist:
        return JsonResponse({"error": "Unidad no encontrada"}, status=404)
    except Estaciones.DoesNotExist:
        return JsonResponse({"error": "Estación no encontrada"}, status=404)

@csrf_exempt
def crear_solicitud_informe(request, id_usuario):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Obtener el usuario asociado al id_usuario
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            
            # Obtener la persona asociada al usuario
            persona = usuario.id_persona
            
            # Obtener el empleado asociado a la persona
            empleado = Empleados.objects.get(id_persona=persona)
            
            # Obtener la última solicitud del empleado
            ultima_solicitud = Solicitudes.objects.filter(id_empleado=empleado).order_by('-id_solicitud').first()
            
            secuencia_informe = 1
            if ultima_solicitud:
                # Obtener el último informe asociado a la última solicitud
                ultima_informe = Informes.objects.filter(id_solicitud=ultima_solicitud).order_by('-secuencia_informe').first()
                if ultima_informe:
                    secuencia_informe = ultima_informe.secuencia_informe + 1

            # Crear la solicitud
            nueva_solicitud = Solicitudes.objects.create(
                fecha_solicitud=datetime.now(),
                motivo_movilizacion=data.get('motivo_movilizacion', ''),
                fecha_salida_solicitud=data.get('fecha_salida_solicitud'),
                hora_salida_solicitud=data.get('hora_salida_solicitud'),
                fecha_llegada_solicitud=data.get('fecha_llegada_solicitud'),
                hora_llegada_solicitud=data.get('hora_llegada_solicitud'),
                descripcion_actividades=data.get('descripcion_actividades', ''),
                listado_empleado=data.get('listado_empleado', ''),
                estado_solicitud='Pendiente',
                id_empleado=empleado
            )

            # Crear el informe asociado
            nuevo_informe = Informes.objects.create(
                id_solicitud=nueva_solicitud,
                secuencia_informe=secuencia_informe,
                fecha_informe=datetime.now(),
                fecha_salida_informe=data.get('fecha_salida_informe'),
                hora_salida_informe=data.get('hora_salida_informe'),
                fecha_llegada_informe=data.get('fecha_llegada_informe'),
                hora_llegada_informe=data.get('hora_llegada_informe'),
                evento=data.get('evento', ''),
                observacion=data.get('observacion', '')
            )

            return JsonResponse({
                'solicitud': {
                    'id_solicitud': nueva_solicitud.id_solicitud,
                    'fecha_solicitud': nueva_solicitud.fecha_solicitud,
                    'motivo_movilizacion': nueva_solicitud.motivo_movilizacion,
                    # Agrega aquí los otros campos que desees devolver
                },
                'informe': {
                    'id_informe': nuevo_informe.id_informes,  # Nombre correcto del campo para el id del informe
                    'secuencia_informe': nuevo_informe.secuencia_informe,
                    'fecha_informe': nuevo_informe.fecha_informe,
                    'evento': nuevo_informe.evento,
                    # Agrega aquí los otros campos que desees devolver
                }
            }, status=201)
        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos JSON inválidos"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


def generar_numero_solicitud(solicitud):
    try:
        empleado = solicitud.id_empleado
        persona = Personas.objects.get(id_persona=empleado.id_persona.id_persona)
        informe = Informes.objects.get(id_solicitud=solicitud.id_solicitud)
        nombres = persona.nombres.split()
        apellidos = persona.apellidos.split()
        unidad = Unidades.objects.get(id_unidad=empleado.id_cargo.id_unidad.id_unidad)
        estacion = Estaciones.objects.get(id_estacion=unidad.id_estacion.id_estacion)

        secuencia_informe = informe.secuencia_informe
        siglas_nombres = nombres[0][:1].upper() + (nombres[1][:1].upper() if len(nombres) >= 2 else '')
        siglas_apellidos = apellidos[0][:1].upper() + (apellidos[1][:1].upper() if len(apellidos) >= 2 else '')
        siglas_unidad = unidad.siglas_unidad
        siglas_estacion = estacion.siglas_estacion
        año_solicitud = datetime.now().year

        numero_solicitud = f"{secuencia_informe:03d}-{siglas_nombres}{siglas_apellidos}-{siglas_unidad}-INIAP-{siglas_estacion}-{año_solicitud}"
        return numero_solicitud
    except Exception as e:
        return str(e)

@csrf_exempt
def listar_solicitudes(request, id_usuario):
    if request.method == 'GET':
        try:
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            empleado = Empleados.objects.get(id_persona=usuario.id_persona)
            solicitudes = Solicitudes.objects.filter(id_empleado=empleado)
            lista_solicitudes = []
            for solicitud in solicitudes:
                numero_solicitud = generar_numero_solicitud(solicitud)
                lista_solicitudes.append({
                    'id_solicitud': solicitud.id_solicitud,
                    'numero_solicitud': numero_solicitud,
                    'fecha_solicitud': solicitud.fecha_solicitud,
                    'motivo_movilizacion': solicitud.motivo_movilizacion,
                    'estado_solicitud': solicitud.estado_solicitud
                })
            return JsonResponse(lista_solicitudes, safe=False)
        except Usuarios.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
        except Empleados.DoesNotExist:
            return JsonResponse({"error": "Empleado no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error interno del servidor: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)

