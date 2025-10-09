from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import os, json
from pymongo import MongoClient

from ..models.route import Route
from ..models.order import Order
from ..db import get_db

# Inicialización
db = get_db()
routes_collection = db['routes']
orders_collection = db['orders']
counters_collection = db['counters']

route_api = Blueprint('route', __name__)

# ---------------------- Configuración archivos ----------------------
UPLOAD_FOLDER = '/home/ubuntu/evidences'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------- Función auxiliar ----------------------
def get_next_route_number():
    counter = counters_collection.find_one_and_update(
        {'_id': 'route_number'},
        {'$inc': {'sequence_value': 1}},
        upsert=True,
        return_document=True
    )
    return counter.get('sequence_value', 1)


# ---------------------- Crear ruta ----------------------
def func_create_route(close_date, cost=0):
    route_number = get_next_route_number()
    orders = list(orders_collection.find({"delivery_date": close_date}))

    if not orders:
        return jsonify({"message": "No orders found for the given delivery date."}), 404

    stops = []
    for index, order in enumerate(orders, start=1):
        total = sum(item['price_sale'] * item['quantity'] for item in order['products'])
        stop = {
            "total_to_charge": total,
            "quantity_sku": len(order['products']),
            "address": order.get('deliveryAddress'),
            "phone": order.get('customer_phone'),
            "client_name": order.get('customer_name'),
            "total_charged": total,
            "payment_method": order.get("paymentMethod"),
            "slot": order.get("deliverySlot"),
            "open_hour": order.get("open_hour"),
            "order": index,
            "order_number": order.get('order_number'),
            "status": "Por entregar",
            "payment_date": order.get('payment_date'),
            "driver_name": order.get('driver_name')
        }
        stops.append(stop)

    route = Route(route_number=route_number, close_date=close_date, stops=stops, cost=cost)
    route_id = route.save()

    return jsonify({'message': 'Route created successfully', 'route_id': str(route_id)}), 201


@route_api.route('/route', methods=['POST'])
def create_route():
    data = request.get_json()
    close_date = data.get('close_date')
    cost = data.get('cost', 0)
    if not close_date:
        return jsonify({'message': 'close_date is required'}), 400
    return func_create_route(close_date, cost)


# ---------------------- Actualizar ruta ----------------------
@route_api.route('/route', methods=['PUT'])
def update_route():
    data = request.form.get('route')
    evidence = request.files.get('evidence')

    if not data:
        return jsonify({'message': 'Missing route data'}), 400

    try:
        route_data = json.loads(data)
    except json.JSONDecodeError:
        return jsonify({'message': 'Invalid JSON format'}), 400

    route_id = route_data.get('id')
    if not route_id:
        return jsonify({'message': 'Missing route ID'}), 400

    existing_route = Route.object(route_id)
    if not existing_route:
        return jsonify({'message': 'Route not found'}), 404

    route_instance = Route(
        id=existing_route['id'],
        route_number=existing_route.get('route_number'),
        close_date=existing_route.get('close_date'),
        cost=existing_route.get('cost'),
        stops=existing_route.get('stops')
    )

    # Actualizar datos
    route_instance.route_number = route_data.get('route_number', route_instance.route_number)
    route_instance.close_date = route_data.get('close_date', route_instance.close_date)
    route_instance.cost = route_data.get('cost', route_instance.cost)
    route_instance.stops = route_data.get('stops', route_instance.stops)

    # Guardar evidencia
    if evidence and allowed_file(evidence.filename):
        filename = secure_filename(evidence.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        evidence.save(filepath)

    route_instance.update()

    # Actualizar órdenes relacionadas
    for stop in route_instance.stops:
        order_number = stop.get('order_number')
        status = stop.get('status')
        if order_number and status:
            orders_collection.update_one(
                {"order_number": order_number},
                {"$set": {"status_payment": status, "totalPayment": stop.get("total_charged")}}
            )

    return jsonify({'message': 'Route updated successfully'}), 200


# ---------------------- Listar rutas ----------------------
@route_api.route('/routes', methods=['GET'])
def list_routes():
    routes_cursor = Route.objects()
    route_data = [
        {
            "id": str(route["_id"]),
            "route_number": route["route_number"],
            "close_date": route["close_date"],
            "stops": route["stops"],
            "status": "creada",
            "cost": route["cost"]
        }
        for route in routes_cursor
    ]
    return jsonify(route_data), 200


# ---------------------- Obtener ruta por número ----------------------
@route_api.route('/route/<string:route_number>', methods=['GET'])
def get_route(route_number):
    route = Route.find_by_route_number(route_number)
    if not route:
        return jsonify({'message': 'Route not found'}), 404
    route['_id'] = str(route['_id'])
    return jsonify(route), 200


# ---------------------- Obtener ruta por fecha ----------------------
@route_api.route('/route/fecha/<string:date>', methods=['GET'])
def get_route_by_date(date):
    route = Route.find_by_date(date)
    if not route:
        return jsonify({'message': 'Route not found'}), 404
    return jsonify(route.to_json()), 200


# ---------------------- Consolidado de ruta ----------------------
@route_api.route('/consolidated/<string:route_number>/', methods=['GET'])
def get_route_consolidated(route_number):
    try:
        route_number = int(route_number)
    except ValueError:
        return jsonify({"error": "route_number debe ser un número"}), 400

    pipeline = [
        {"$match": {"route_number": route_number}},
        {"$unwind": "$stops"},
        {"$lookup": {
            "from": "orders",
            "localField": "stops.order_number",
            "foreignField": "order_number",
            "as": "order_data"
        }},
        {"$unwind": {"path": "$order_data", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "order_total_quantity": {
                "$sum": {
                    "$map": {
                        "input": {"$ifNull": ["$order_data.products", []]},
                        "as": "prod",
                        "in": "$$prod.quantity"
                    }
                }
            }
        }},
        {"$group": {
            "_id": "$stops.driver_name",
            "cantidad_stops": {"$sum": 1},
            "dinero_por_metodo": {
                "$push": {
                    "metodo": "$stops.payment_method",
                    "valor": "$stops.total_to_charge"
                }
            },
            "cantidad_sku": {"$sum": "$stops.quantity_sku"},
            "total_products_quantity": {"$sum": "$order_total_quantity"}
        }},
        {"$project": {
            "_id": 0,
            "driver_name": "$_id",
            "cantidad_stops": 1,
            "cantidad_sku": 1,
            "total_products_quantity": 1,
            "dinero_por_metodo": 1
        }}
    ]

    resultados = list(routes_collection.aggregate(pipeline))
    return jsonify(resultados), 200


# ---------------------- Eliminar ruta ----------------------
@route_api.route('/route/<string:route_id>', methods=['DELETE'])
def delete_route(route_id):
    route_data = Route.object(route_id)
    if not route_data:
        return jsonify({'message': 'Route not found'}), 404

    route_instance = Route(
        id=route_data['id'],
        route_number=route_data.get('route_number'),
        close_date=route_data.get('close_date'),
        cost=route_data.get('cost'),
        stops=route_data.get('stops')
    )

    route_instance.delete_route()
    return jsonify({'message': 'Route deleted successfully'}), 200


# ---------------------- Obtener evidencia ----------------------
@route_api.route('/route/evidence/<string:filename>', methods=['GET'])
def get_evidence(filename):
    if not allowed_file(filename):
        return jsonify({'message': 'Invalid file type'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'message': 'Evidence file not found'}), 404

    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------------------- Obtener stop por número de orden ----------------------
@route_api.route('/stop_order_number/<string:order_number>', methods=['GET'])
def get_stop_order(order_number):
    order = Order.find_by_order_number(order_number)
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    route = Route.find_by_date(order.delivery_date)
    if not route:
        return jsonify({'message': 'Route not found for this order'}), 404

    for stop in route.stops:
        if stop.get("order_number") == str(order_number):
            return jsonify(stop), 200

    return jsonify({'message': 'Stop not found in this route'}), 404
