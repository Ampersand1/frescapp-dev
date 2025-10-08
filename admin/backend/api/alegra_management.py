from flask import Blueprint, jsonify, request
from ..models.customer import Customer
import json
from flask_bcrypt import Bcrypt
from datetime import datetime
import requests
from datetime import datetime
from pymongo import MongoClient
from ..models.order import Order

alegra_api = Blueprint('alegra', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
collection = db['orders']
purchases = db['purchases']
invoice_counter = db['invoice_counter'] 

# URL base y cabeceras para la API de Alegra
url_clients = "https://api.alegra.com/api/v1/contacts"
url_items = "https://api.alegra.com/api/v1/items"
url_doc_soportes = "https://api.alegra.com/api/v1/bills"
url_suppliers = "https://api.alegra.com/api/v1/contacts"
headers = {
    "accept": "application/json",
    "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"  # Reemplaza esto con tus credenciales
}
def get_all_clients():
    clients = []
    start = 0
    limit = 30
    while True:
        response = requests.get(f"{url_clients}?start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            clients.extend(data)
            start += limit
        else:
            print(f"Error al obtener la lista de clientes: {response.status_code} - {response.text}")
            break
    return clients

# Función para obtener todos los productos con paginación
def get_all_items():
    items = []
    start = 0
    limit = 30
    while True:
        response = requests.get(f"{url_items}?start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            items.extend(data)
            start += limit
        else:
            print(f"Error al obtener la lista de productos: {response.status_code} - {response.text}")
            break
    return items

# Función para buscar el cliente en la lista por identificación
def find_client_by_identification(clients, identification):
    for client in clients:
        if client.get("identificationObject", {}).get("number") == identification:
            return client
    return None

# Función para buscar el producto en la lista por referencia
def find_item_by_reference(items, reference):
    for item in items:
        if item.get("reference") == reference:
            return item
    return None

# Función para transformar y enviar la factura
def transform_and_send_invoice(order, client, items):
    client_data = {
        "id": client["id"],  
        "name": client["name"],
        "identification": client["identificationObject"]["number"],
        "phonePrimary": client["phonePrimary"],
        "email": client["email"],
        "address": {
            "address": client["address"]["address"],
            "department": client["address"]["department"],
            "city": client["address"]["city"]
        },
        "kindOfPerson": client["kindOfPerson"],
        "regime": client["regime"],
        "identificationObject": client["identificationObject"]
    }

    items_data = []
    for product in sorted(list(order['products']), key=lambda x: x['name']):
        item = find_item_by_reference(items, product["sku"])
        if item:
            items_data.append({
                "id": item["id"],
                "name": product["name"],
                "description": "",
                "price": product["price_sale"],
                "discount": 0,
                "reference": product["sku"],
                "quantity": product["quantity"],
                "unit": "unit",
                "tax": [],
                "total": product["price_sale"] * product["quantity"]
            })

    invoice_data = {
        "id": order["order_number"],  # Este campo debe ser único para cada factura
        "date": order["delivery_date"],
        "dueDate": order["delivery_date"],
        "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "observations": None,
        "anotation": "",
        "termsConditions": "Esta factura se asimila en todos sus efectos a una letra de cambio de conformidad con el Art. 774 del código de comercio. Autorizo que en caso de incumplimiento de esta obligación sea reportado a las centrales de riesgo, se cobraran intereses por mora.",
        "status": "open",
        "client": client_data,
        "purchaseOrderNumber":  str(order["order_number"]),
        "numberTemplate": {
            "id": "16",
            "prefix": "FRES",
            "number": order["order_number"],
            "text": "Autorización de numeración de facturación N°18764069939613 de 2024-04-30 Modalidad Factura Electrónica Desde N° FRES1100 hasta FRES3500 con vigencia hasta 2026-04-30",
            "documentType": "invoice",
            "fullNumber": f"FRES{order['order_number']}",
            "formattedNumber": order["order_number"],
            "isElectronic": True
        },
        "subtotal": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
        "discount": order["discount"],
        "tax": 0,
        "total": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
        "totalPaid": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
        "balance": 0,
        "decimalPrecision": "0",
        "warehouse": {
            "id": "1",
            "name": "Principal"
        },
        "term": "De contado",
        "type": "NATIONAL",
        "operationType": "STANDARD",
        "paymentForm": "CASH",
        "paymentMethod": "CASH",
        "payments": [
        {
            "amount": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
            "paymentMethod": "cash",
            "date": order["delivery_date"],
            "account": { "id": 1 },
        }
        ],
        "seller": None,
        "priceList": {
            "id": 1,
            "name": "General"
        },
        "stamp": {
            "legalStatus": "PENDING",
            "cufe": "216598b481686b59cc4681f36faeb20228f1f53521c1c605b98722abee530405264984a51544241708d8bf4de7ef3bee",
            "barCodeContent": "NumFac: FRES1281\nFecFac: 2024-07-10\nHorFac: 21:29:49-05:00\nNitFac: 901387528\nDocAdq: 1020808385\nValFac: 165000.00\nValIva: 0.00\nValOtroIm: 0.00\nValTolFac: 165000.00\nCUFE: 216598b481686b59cc4681f36faeb20228f1f53521c1c605b98722abee530405264984a51544241708d8bf4de7ef3bee\nQRCode: https:\/\/catalogo-vpfe.dian.gov.co\/document\/searchqr?documentkey=216598b481686b59cc4681f36faeb20228f1f53521c1c605b98722abee530405264984a51544241708d8bf4de7ef3bee\n",
            "date": "2024-07-10 21:30:52",
            "warnings": [
                "Regla: FAZ09, Notificación: Debe existir el grupo de información de identificación del bien o servicio",
                "Regla: FAJ43b, Notificación: Nombre informado No corresponde al registrado en el RUT con respecto al Nit suministrado.",
                "Regla: FAJ43b, Notificación: Nombre informado No corresponde al registrado en el RUT con respecto al Nit suministrado.",
                "Regla: RUT01, Notificación: La validación del estado del RUT próximamente estará disponible.",
                "Regla: RUT01, Notificación: La validación del estado del RUT próximamente estará disponible."
            ]
        },

        "items": items_data,
        "costCenter": None,
        "printingTemplate": {
            "id": "7",
            "name": "Clásico (Carta electrónica)",
            "pageSize": "letter"
        }
    }
    # URL y cabeceras para la API de Alegra
    url_invoice = "https://api.alegra.com/api/v1/invoices/"
    response = requests.post(url_invoice, headers=headers, json=invoice_data)
    return response

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

def find_supplier_by_nit(suppliers, nit):
    return next((supplier for supplier in suppliers if str(supplier.get("identification")) == nit), None)

def find_item_by_reference(items, reference):
    return next((item for item in items if item.get("reference") == reference), None)

def get_and_increment_invoice_number():
    invoice_data = invoice_counter.find_one_and_update({}, {"$inc": {"last_invoice": 1}}, upsert=True, return_document=True)
    return invoice_data['last_invoice']

def func_send_invoice(order_number):
    order = collection.find_one({"order_number": order_number})
    if order:
        clients = get_all_clients()
        items = get_all_items()
        client = find_client_by_identification(clients,order["customer_documentNumber"].split("-")[0])        
        if client:
            res = transform_and_send_invoice(order, client, items)
            if str(res.status_code) == '201':
                collection.update_one(
                    {"order_number": order_number},
                    {"$set": {"alegra_id":res.json().get("id")}}
                )
                return jsonify({"message": res.text}), res.status_code
            else:
                return jsonify({"message": res.text}), res.status_code
        else:
            return jsonify({"message": f"No se encontró un cliente con identificación {order['customer_documentNumber']}"}), 400

    else:
        return jsonify({"message": f"No se encontró la orden con número {order_number}"}), 400

def func_send_purchase(fecha):
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
                subtotal = producto['final_price_purchase'] * producto['total_quantity']

                # Crear el item del producto
                item_info = {
                    "id": item_alegra['id'],
                    "name": item_alegra['name'],
                    "price": producto['final_price_purchase'],
                    "quantity": producto['total_quantity'],
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

    facturas_creadas = []
    errores = []

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
            "date": fecha,
            "dueDate": fecha,
            "provider": int(purchase['proveedor_id']),
            "paymentMethod": "CASH",
            "paymentType": "CASH",
            "termsConditions": "Autorización de numeración de facturación",
            "payments": [
                {
                    "account": { "id": 1 },
                    "date": fecha,
                    "amount": total,
                    "paymentMethod": "cash"
                }
            ]
        }

        response = requests.post(url_doc_soportes, headers=headers, json=payload)
            # Actualizar en MongoDB
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

        purchases.update_many(
            {"products.proveedor.nit": purchase['proveedor_nit'], "date": fecha},
            {
                "$set": {"status": "Facturada"}
            }
        )

        facturas_creadas.append({
            "proveedor_name": purchase['proveedor_name'],
            "invoice_number": invoice_number
        })
    else:
        errores.append({
            "proveedor_name": purchase['proveedor_name'],
            "error": response.text
        })
    return jsonify({
        "facturas_creadas": facturas_creadas,
        "errores": errores
    }), 200 

def emit_invoice(alegra_id):
    url = 'https://api.alegra.com/api/v1/invoices/stamp' 

    # Encabezados de la petición
    headers = {
        "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"
    }
    payload = {'ids': [alegra_id]}  # Reemplaza con los IDs de las facturas que deseas timbrar
    # Realizar la solicitud GET
    response = requests.post(url, headers=headers, json=payload)

@alegra_api.route('/send_invoice/<string:order_number>', methods=['GET'])
def send_invoice(order_number):
    return func_send_invoice(order_number)
@alegra_api.route('/get_invoice/<string:order_number>', methods=['GET'])
def get_invoice(order_number):
    orden = Order.find_by_order_number(order_number)
    url = f"https://api.alegra.com/api/v1/invoices/{orden.alegra_id}?fields=pdf"
    headers = {
        "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"
    }
    response = requests.get(url, headers=headers, stream=True)
    return jsonify(response.json().get('pdf'))

@alegra_api.route('/send_purchase/<string:fecha>', methods=['GET'])
def send_purchase(fecha):
    return func_send_purchase(fecha)
