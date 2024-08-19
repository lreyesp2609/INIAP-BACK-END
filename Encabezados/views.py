import base64
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Encabezados
from django.conf import settings
import jwt

@method_decorator(csrf_exempt, name='dispatch')
class CrearEncabezadoView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'Token no proporcionado'}, status=400)

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expirado'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Token inválido'}, status=401)

            # Obtener archivos del formulario (opcional)
            encabezado_superior_file = request.FILES.get('encabezado_superior')
            encabezado_inferior_file = request.FILES.get('encabezado_inferior')

            def convert_file_to_base64(file):
                try:
                    file_content = file.read()
                    file_base64 = base64.b64encode(file_content).decode('utf-8')
                    format = file.content_type.split('/')[1]  # Por ejemplo, 'jpeg', 'png'
                    return f"data:image/{format};base64,{file_base64}"
                except Exception as e:
                    raise ValueError("Error al convertir el archivo a base64: " + str(e))

            # Convertir archivos a base64 si están presentes
            encabezado_superior_base64 = ""
            encabezado_inferior_base64 = ""

            if encabezado_superior_file:
                try:
                    encabezado_superior_base64 = convert_file_to_base64(encabezado_superior_file)
                except ValueError as e:
                    return JsonResponse({'error': str(e)}, status=400)
            
            if encabezado_inferior_file:
                try:
                    encabezado_inferior_base64 = convert_file_to_base64(encabezado_inferior_file)
                except ValueError as e:
                    return JsonResponse({'error': str(e)}, status=400)

            # Eliminar encabezados existentes
            Encabezados.objects.all().delete()

            # Crear encabezado en la base de datos
            try:
                encabezado = Encabezados.objects.create(
                    encabezado_superior=encabezado_superior_base64,
                    encabezado_inferior=encabezado_inferior_base64
                )
            except Exception as e:
                return JsonResponse({'error': f'Error al guardar el encabezado: {str(e)}'}, status=500)

            return JsonResponse({'mensaje': 'Encabezado creado exitosamente', 'id_encabezado': encabezado.id_encabezado}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
