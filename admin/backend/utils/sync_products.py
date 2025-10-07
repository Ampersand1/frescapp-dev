import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
import json
from pymongo import MongoClient
from flask import Blueprint, jsonify, request

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]

def authenticate():
    try:
        if os.name == 'posix':  # Linux o macOS
            path_file = '/home/ubuntu/frescapp/admin/backend/utils/'
        elif os.name == 'nt':  # Windows
            path_file = 'C:/Users/USUARIO/Documents/frescapp/admin/backend/utils/'
        else:
            raise EnvironmentError("Unsupported OS")
            
        credential_path = os.path.join(path_file, 'credentials_spread.json')
        if not os.path.exists(credential_path):
            raise FileNotFoundError(f"El archivo de credenciales no se encontró en {credential_path}")
        
        creds = Credentials.from_service_account_file(credential_path, scopes=scope)
        return creds
    except Exception as e:
        print({'error': str(e)})
try:
    credentials = authenticate()
    if isinstance(credentials, tuple):
        print(credentials)
    client = gspread.authorize(credentials)
except Exception as e:
    print(jsonify({'error': f"Error al autorizar con Google Sheets: {str(e)}"}))
try:
    spreadsheet_id = "1efvIDyxsO0n2A4P_lZj1BUNy-SV_5d5zm9m8CMUI9mc"
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.get_worksheet(0)
    records = worksheet.get_all_records()
except Exception as e:
    print(jsonify({'error': f"Error al acceder a Google Sheets: {str(e)}"}))
try:
    df = pd.DataFrame(records)
    df = df[df['status'] == 'active']
    df = df.drop(columns=['pricing'], errors='ignore')
    df['iva'] = df['iva'].astype(bool)
    df['quantity'] = 0
    json_data = df.to_json(orient='records', date_format='iso')
except Exception as e:
    print("Error al procesar datos de Google Sheets")

try:
    mongo_client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
    db = mongo_client['frescapp']
    collection = db['products']
    collection.delete_many({})
    data = json.loads(json_data)
    collection.insert_many(data)
    collection.update_many(
        {},
        [
            { '$set': { 'price_sale': { '$toDouble': "$price_sale" } } },
            { '$set': { 'discount': { '$toDouble': "$discount" } } },
            { '$set': { 'margen': { '$toDouble': "$margen" } } },
            { '$set': { 'iva_value': { '$toDouble': "$iva_value" } } },
            { '$set': { 'price_purchase': { '$toDouble': "$price_purchase" } } },
            { '$set': { 'description': { '$toString': "$description" } } },
            { '$set': { 'root': { '$toString': "$root" } } },
            { '$set': { 'quantity': { '$toDouble': "$quantity" } } },
            { '$set': { 'step_unit': { '$toDouble': "$step_unit" } } },
        ]
    )
except Exception as e:
    print("Error al interactuar con MongoDB"+str(e))
