from flask import Blueprint, jsonify, request
from ..models.customer import Customer
from ..models.product import Product
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime
import requests
from datetime import datetime
from pymongo import MongoClient
import pytz

consumer_key = 'ck_203177d4d7a291000f60cd669ab7cb98976b3620'
consumer_secret = 'cs_d660a52cd323666cad9b600a9d61ed6c577cd6f9'
woo_api = Blueprint('woo', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
collection = db['orders']
def transform_order(order):
    date_str = next((item["value"] for item in order["meta_data"] if item["key"] == "Fecha de entrega"),"")
    month_mapping = {
        'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
        'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
        'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'
    }

    if date_str:
        # Eliminar la coma y dividir la cadena en partes
        date_str_clean = date_str.replace(',', '')
        day, month_name, year = date_str_clean.split(' ')

        # Obtener el número del mes usando el diccionario
        month = month_mapping[month_name]

        # Crear la cadena en el formato 'YYYY-MM-DD'
        formatted_date_str = f"{year}-{month}-{day.zfill(2)}"
        products = []
        for item in order["line_items"]:
            product_data = Product.find_by_sku(sku=item["sku"])  # Asegúrate de que esta función exista y retorne un dict o None

            unit = product_data.get("unit") if product_data else ""
            category = product_data.get("category") if product_data else ""

            products.append({
                "sku": item["sku"],
                "name": item["name"],
                "price_sale": item["price"],
                "quantity": item["quantity"],
                "iva": False,
                "iva_value": 0,
                "unit": unit or "",
                "category": category or ""
            })
    transformed_order = {
        "order_number": order["number"],
        "customer_email": order["billing"]["email"],
        "customer_phone": order["billing"]["phone"],
        "customer_documentNumber": next((item["value"] for item in order["meta_data"] if item["key"] == "_billing_"), ""),
        "customer_documentType": "NIT",
        "customer_name": f"{order['billing']['first_name']} {order['billing']['last_name']}",
        "delivery_date": formatted_date_str,
        "status": "Creada",
        "created_at": datetime.strptime(order["date_created"], "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d'),
        "updated_at": datetime.strptime(order["date_modified"], "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d'),
        "products": products,
        "total": int(order["total"]),
        "deliverySlot": next((item["value"] for item in order["meta_data"] if item["key"] == "_orddd_time_slot"), ""),
        "paymentMethod": order["payment_method_title"],
        "deliveryAddress": order["shipping"]["address_1"],
        "deliveryAddressDetails": order["shipping"]["address_2"],
        "discount": 0,
        "deliveryCost": 0,
        "alegra_id" : "000",
        "payment_date": "",
        "driver_name": "",
        "seller_name": "",
        "source":"Página",
        "totalPayment" : 0,
        "open_hour": ""
    }
    return transformed_order

# Función para obtener y procesar órdenes
def process_orders(order_number):
    if not collection.find_one({"order_number": order_number}):
        url = f'https://www.buyfrescapp.com/wp-json/wc/v3/orders/{order_number}?consumer_key={consumer_key}&consumer_secret={consumer_secret}'
        response = requests.get(f'{url}&number={order_number}')
        if response.status_code == 200:
            orders = response.json()
            transformed_order = transform_order(orders)
            collection.insert_one(transformed_order)
            return jsonify({"message" : f"Orden {order_number} procesada y guardada en MongoDB"}),200
        else:
            return jsonify({"message" : f"Error al obtener la orden {order_number}: {response.status_code}"}),400
    else:
        return jsonify({"message" : f"La orden {order_number} ya existe en la base de datos."}),200


@woo_api.route('/get_order/<string:order_number>', methods=['GET'])
def get_order(order_number):
    return process_orders(order_number)