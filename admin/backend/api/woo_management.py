from flask import Blueprint, jsonify, request
from ..models.customer import Customer
from ..models.product import Product
from datetime import datetime
import requests
from ..db import get_db

woo_api = Blueprint('woo', __name__)
db = get_db()
orders_collection = db['orders']

# ⚙️ En producción deben estar en variables de entorno
CONSUMER_KEY = 'ck_203177d4d7a291000f60cd669ab7cb98976b3620'
CONSUMER_SECRET = 'cs_d660a52cd323666cad9b600a9d61ed6c577cd6f9'

# ---------------------------------------------
# 🔁 Función auxiliar: transformar orden WooCommerce a formato interno
# ---------------------------------------------
def transform_order(order):
    # Buscar la fecha de entrega en meta_data
    date_str = next((item.get("value") for item in order.get("meta_data", []) if item.get("key") == "Fecha de entrega"), "")
    formatted_date_str = ""

    month_mapping = {
        'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
        'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
        'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'
    }

    if date_str:
        try:
            # Limpiar y dividir la fecha
            date_str_clean = date_str.replace(',', '').strip()
            day, month_name, year = date_str_clean.split(' ')
            month = month_mapping.get(month_name)
            formatted_date_str = f"{year}-{month}-{day.zfill(2)}"
        except Exception:
            formatted_date_str = datetime.utcnow().strftime('%Y-%m-%d')

    # Procesar productos
    products = []
    for item in order.get("line_items", []):
        product_data = Product.find_by_sku(sku=item.get("sku"))
        unit = product_data.get("unit") if product_data else ""
        category = product_data.get("category") if product_data else ""
        products.append({
            "sku": item.get("sku", ""),
            "name": item.get("name", ""),
            "price_sale": item.get("price", 0),
            "quantity": item.get("quantity", 0),
            "iva": False,
            "iva_value": 0,
            "unit": unit,
            "category": category
        })

    transformed_order = {
        "order_number": order.get("number"),
        "customer_email": order.get("billing", {}).get("email", ""),
        "customer_phone": order.get("billing", {}).get("phone", ""),
        "customer_documentNumber": next((m.get("value") for m in order.get("meta_data", []) if "document" in m.get("key", "").lower()), ""),
        "customer_documentType": "NIT",
        "customer_name": f"{order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}",
        "delivery_date": formatted_date_str,
        "status": "Creada",
        "created_at": datetime.strptime(order.get("date_created", "")[:19], "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d') if order.get("date_created") else "",
        "updated_at": datetime.strptime(order.get("date_modified", "")[:19], "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d') if order.get("date_modified") else "",
        "products": products,
        "total": int(float(order.get("total", 0))),
        "deliverySlot": next((m.get("value") for m in order.get("meta_data", []) if m.get("key") == "_orddd_time_slot"), ""),
        "paymentMethod": order.get("payment_method_title", ""),
        "deliveryAddress": order.get("shipping", {}).get("address_1", ""),
        "deliveryAddressDetails": order.get("shipping", {}).get("address_2", ""),
        "discount": 0,
        "deliveryCost": 0,
        "alegra_id": "000",
        "payment_date": "",
        "driver_name": "",
        "seller_name": "",
        "source": "Página",
        "totalPayment": 0,
        "open_hour": ""
    }

    return transformed_order


# ---------------------------------------------
# 🔁 Función para obtener y guardar orden de WooCommerce
# ---------------------------------------------
def fetch_and_save_order(order_number):
    """Obtiene una orden desde WooCommerce y la guarda en MongoDB."""
    if orders_collection.find_one({"order_number": order_number}):
        return {"message": f"La orden {order_number} ya existe en la base de datos."}, 200

    url = f"https://www.buyfrescapp.com/wp-json/wc/v3/orders/{order_number}"
    params = {"consumer_key": CONSUMER_KEY, "consumer_secret": CONSUMER_SECRET}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"message": f"Error al obtener la orden {order_number}: {response.status_code}"}, 400

    order_data = response.json()
    transformed = transform_order(order_data)
    orders_collection.insert_one(transformed)

    return {"message": f"Orden {order_number} procesada y guardada en MongoDB"}, 200


# ---------------------------------------------
# 📦 Endpoint público
# ---------------------------------------------
@woo_api.route('/get_order/<string:order_number>', methods=['GET'])
def get_order(order_number):
    message, status = fetch_and_save_order(order_number)
    return jsonify(message), status
