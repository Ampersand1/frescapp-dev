import csv
import json
from datetime import datetime

# Función para leer el archivo CSV y convertir los registros en un formato JSON
def csv_to_json(csv_file_path, json_file_path):
    json_data = []
    with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for idx, row in enumerate(csv_reader):
            action = {
                "actionNumber": str(idx + 1),
                "dateAction": row["dateAction"],
                "dateSolution": row["dateSolution"],
                "type": {
                    "name": row["name_action"],
                    "requiresOrder": row["requiresOrder"].lower() == 'true',
                    "solutions": row["solutions"].split(',')  # Soluciones separadas por comas
                },
                "customer": {
                    "name": row["name_customer"],
                    "email": row["email"],
                    "phone": row["phone"],
                    "address": row["address"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "document_type": row["documnet_type"],
                    "document": row["document"],
                    "category": row["category"],
                    "micro_category": row["micro_category"]
                },
                "orderNumber": "",  # Valor por defecto
                "manager": row["manager"],
                "status": row["status"],
                "actionComment": row["actionComment"],
                "solutionType": row["solutionType"],
                "solutionComment": row["solutionComment"]
            }
            json_data.append(action)
    
    # Escribir los datos en un archivo JSON
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)

# Ruta del archivo CSV de entrada
csv_file_path = 'actions.csv'

# Ruta del archivo JSON de salida
json_file_path = 'actions.json'

# Convertir el archivo CSV a JSON
csv_to_json(csv_file_path, json_file_path)

print(f"Archivo JSON generado en: {json_file_path}")
