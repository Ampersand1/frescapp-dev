from flask import Blueprint, jsonify, request
import requests
from pymongo import MongoClient
from collections import defaultdict

# Configuración del Blueprint de Flask
alegra_api = Blueprint('alegra', __name__)

# Conexión con MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
purchases = db['purchases']
invoice_counter = db['invoice_counter']  # Colección para almacenar el número de la factura

# URLs de la API de Alegra
url_doc_soportes = "https://api.alegra.com/api/v1/bills"
url_suppliers = "https://api.alegra.com/api/v1/contacts"
url_items = "https://api.alegra.com/api/v1/items"

# Cabeceras para la API de Alegra
headers = {
    "accept": "application/json",
    "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"  # Reemplaza esto con tus credenciales
}

# Función para obtener todos los proveedores de Alegra
def get_all_suppliers():
    suppliers = []
    start, limit = 0, 30
    while True:
        response = requests.get(f"{url_suppliers}?type=provider&start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            suppliers.extend(data)
            start += limit
        else:
            print(f"Error al obtener proveedores: {response.status_code} - {response.text}")
            break
    return suppliers

# Función para obtener todos los ítems de Alegra
def get_all_items():
    items = []
    start, limit = 0, 30
    while True:
        response = requests.get(f"{url_items}?start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            items.extend(data)
            start += limit
        else:
            print(f"Error al obtener productos: {response.status_code} - {response.text}")
            break
    return items

def find_supplier_by_nit(suppliers, nit):
    return next((supplier for supplier in suppliers if str(supplier.get("identification")) == nit), None)

def find_item_by_reference(items, reference):
    return next((item for item in items if item.get("reference") == reference), None)

# Función para obtener y actualizar el número de factura
def get_and_increment_invoice_number():
    # Recuperar el último número de la base de datos
    invoice_data = invoice_counter.find_one_and_update({}, {"$inc": {"last_invoice": 1}}, upsert=True, return_document=True)
    return invoice_data['last_invoice']

def obtener_compras_agrupadas(fecha, fecha_final=None):
    order = purchases.find_one({"date": fecha})
    suppliers = get_all_suppliers()
    items = get_all_items()
    
    grouped_purchases = {}

    for producto in order['products']:
        proveedor_local = producto.get('proveedor')
        if isinstance(proveedor_local, dict) and proveedor_local.get('nit'):
            proveedor_alegra = find_supplier_by_nit(suppliers, proveedor_local.get('nit'))
            item_alegra = find_item_by_reference(items, producto['sku'])
            
            if proveedor_alegra and item_alegra and producto['final_price_purchase'] > 0 and producto['status'] == 'Registrado' and producto['proveedor']['typeSupport'] == 'Documento soporte':
                subtotal = producto['final_price_purchase'] * producto['total_quantity_ordered']

                # Crear el item del producto
                item_info = {
                    "id": item_alegra['id'],
                    "name": item_alegra['name'],
                    "price": producto['final_price_purchase'],
                    "quantity": producto['total_quantity_ordered'],
                    "subtotal": subtotal,
                    "total": subtotal
                }

                # Agrupar productos por proveedor
                if proveedor_alegra['id'] in grouped_purchases:
                    grouped_purchases[proveedor_alegra['id']]['items'].append(item_info)
                else:
                    grouped_purchases[proveedor_alegra['id']] = {
                        "proveedor_id": proveedor_alegra['id'],
                        "proveedor_name": proveedor_alegra['name'],
                        "proveedor_nit": proveedor_alegra['identification'],
                        "items": [item_info]
                    }

    # Convertir el diccionario a una lista
    grouped_purchases_list = [value for value in grouped_purchases.values()]

    # Realizar las llamadas a la API y actualizar estado en MongoDB
    for purchase in grouped_purchases_list:
        # Obtener el número de factura incremental
        invoice_number = get_and_increment_invoice_number()

        # Calcular el total de la factura sumando los subtotales de los ítems
        total = sum(item['subtotal'] for item in purchase['items'])

        payload = {
            "numberTemplate": {
                "number": str(invoice_number),  
                "id": "17"  
            },
            "purchases": {"items": purchase['items']},
            "stamp": {"generateStamp": True},
            "billOperationType": "INDIVIDUAL",
            "date": fecha_final,
            "dueDate": fecha_final,
            "provider": int(purchase['proveedor_id']),
            "paymentMethod": "CASH",
            "paymentType": "CASH",
            "termsConditions": "Autorización de numeración de facturación",
            "payments": [
                {
                    "account": { "id": 1 },
                    "date": fecha_final,
                    "amount": total,
                    "paymentMethod": "cash"
                }
            ]
        }
        response = requests.post(url_doc_soportes, headers=headers, json=payload)
        if response.status_code == 201:
            print(f"Factura creada para {purchase['proveedor_name']} con número {invoice_number}")
            purchases.update_many(
                {"products.proveedor.nit": purchase['proveedor_nit'], "date": fecha},
                {
                    "$set": {
                        "products.$[elem].invoice": invoice_number, 
                        "products.$[elem].status": "Facturada"
                    }
                },
                array_filters=[{"elem.proveedor.nit": purchase['proveedor_nit']}]
            )

            # Actualizar el estado general de la compra fuera del array
            purchases.update_many(
                {"products.proveedor.nit": purchase['proveedor_nit'], "date": fecha},
                {
                    "$set": {"status": "Facturada"}
                }
            )
        else:
            print(f"Error al crear factura: {response.text}")
list_days = ['2025-05-17']
for day in list_days:
    print(f"Procesando compras del día {day}")
    obtener_compras_agrupadas(day,'2025-05-17')
