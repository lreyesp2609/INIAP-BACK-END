import pandas as pd
import requests
import jwt
import os

# Ruta al archivo Excel
file_path = os.path.join(os.getcwd(), 'inyecciónSQL/Unidades/Listado personal SP.xlsx')
df = pd.read_excel(file_path, engine='openpyxl')

# URL de la API
url = 'http://127.0.0.1:8000/Unidades/crear-unidades/1/1/'  # Ajusta la URL según sea necesario

# Token de autorización
headers = {
    'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF91c3VhcmlvIjoxLCJub21icmVfdXN1YXJpbyI6Imx1aXMucmV5ZXMiLCJyb2wiOiJTdXBlclVzdWFyaW8ifQ.sXIpMoxa1g6QxkI98J91XIb7FabqZNnDounB-0E-Pqk',  # Sustituye con el token adecuado
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Iterar sobre cada fila del DataFrame
for index, row in df.iterrows():
    data = {
        'nombre_unidad': row['ÁREA']  # Ajusta el nombre del campo según sea necesario
    }

    # Enviar la solicitud POST
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        print(f"Unidad creada exitosamente: {response.json()}")
    else:
        print(f"Error al crear unidad: {response.json()}")
