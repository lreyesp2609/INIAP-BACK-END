import pandas as pd
import requests
import os

# Ruta al archivo Excel
file_path = os.path.join(os.getcwd(), 'inyecciónSQL/Vehiculos/BASE DE DATOS VEHICULOS EETP.xlsx')
df = pd.read_excel(file_path, engine='openpyxl')

url = 'http://127.0.0.1:8000/Vehiculos/crear-vehiculo/1/'
headers = {
    'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF91c3VhcmlvIjoxLCJub21icmVfdXN1YXJpbyI6Imx1aXMucmV5ZXMiLCJyb2wiOiJTdXBlclVzdWFyaW8ifQ.sXIpMoxa1g6QxkI98J91XIb7FabqZNnDounB-0E-Pqk',  # Sustituye con el token adecuado
    'Content-Type': 'application/x-www-form-urlencoded'
}

for index, row in df.iterrows():
    data = {
        'id_subcategoria_bien': 1,  # Ajusta según sea necesario
        'placa': row['Placa'],
        'codigo_inventario': None,
        'modelo': None,
        'marca': row['MARCA'],
        'color_primario': row['COLOR'],
        'color_secundario': None,
        'anio_fabricacion': row['Año de Fabricación'],
        'numero_motor': row['Nº Motor'],
        'numero_chasis': row['Nº Chasis'],
        'numero_matricula': None,
    }

    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 201:
        print(f"Vehículo creado exitosamente: {response.json()}")
    else:
        print(f"Error al crear vehículo: {response.json()}")
