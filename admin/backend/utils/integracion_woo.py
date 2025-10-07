import requests
import json
from datetime import datetime
from pymongo import MongoClient

consumer_key = 'ck_203177d4d7a291000f60cd669ab7cb98976b3620'
consumer_secret = 'cs_d660a52cd323666cad9b600a9d61ed6c577cd6f9'
url = f'https://www.buyfrescapp.com/wp-json/wc/v3/orders?consumer_key={consumer_key}&consumer_secret={consumer_secret}'

# Conexión a la base de datos MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
collection = db['orders']

# Función para transformar una orden
def transform_order(order):
    transformed_order = {
        "order_number": order["number"],
        "customer_email": order["billing"]["email"],
        "customer_phone": order["billing"]["phone"],
        "customer_documentNumber": next((item["value"] for item in order["meta_data"] if item["key"] == "_billing_"), ""),
        "customer_documentType": "NIT",
        "customer_name": f"{order['billing']['first_name']} {order['billing']['last_name']}",
        "delivery_date": datetime.fromtimestamp(int(next((item["value"] for item in order["meta_data"] if item["key"] == "_orddd_lite_timestamp"), 0))).strftime('%Y-%m-%d'),
        "status": "Creada",
        "created_at": datetime.strptime(order["date_created"], "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d'),
        "updated_at": datetime.strptime(order["date_modified"], "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d'),
        "products": [
            {
                "sku": item["sku"],
                "name": item["name"],
                "price_sale": item["price"],
                "quantity": item["quantity"],
                "iva": False,
                "iva_value": 0
            } for item in order["line_items"]
        ],
        "total": int(order["total"]),
        "deliverySlot": next((item["value"] for item in order["meta_data"] if item["key"] == "_orddd_time_slot"), ""),
        "paymentMethod": order["payment_method_title"],
        "deliveryAddress": order["shipping"]["address_1"],
        "deliveryAddressDetails": order["shipping"]["address_2"],
        "discount": 0,
        "deliveryCost": 0
    }
    return transformed_order

# Función para obtener y procesar órdenes
def process_orders(order_numbers):
    for order_number in order_numbers:
        # Verificar si la orden ya existe en la base de datos
        if not collection.find_one({"order_number": order_number}):
            # Obtener la orden desde el API
            response = requests.get(f'{url}&number={order_number}')
            if response.status_code == 200:
                orders = response.json()
                for order in orders:
                    transformed_order = transform_order(order)
                    collection.insert_one(transformed_order)
                print(f"Orden {order_number} procesada y guardada en MongoDB")
            else:
                print(f"Error al obtener la orden {order_number}: {response.status_code}")
        else:
            print(f"La orden {order_number} ya existe en la base de datos.")


order_numbers = ["8895"]  # Ejemplo de números de orden


# Procesar y guardar las órdenes en MongoDB
process_orders(order_numbers)
