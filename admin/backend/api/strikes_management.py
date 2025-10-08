# app/api/strikes_management.py

from flask import Blueprint, jsonify, request
from ..models.strike import Strike
from ..models.order import Order
from ..models.route import Route

strike_api = Blueprint('strikes', __name__)

@strike_api.route('', methods=['GET'])
def list_strikes():
    order_number = request.args.get('order_number')
    if order_number:
        strikes = Strike.find_by_order(order_number)
    else:
        strikes = Strike.all()
    return jsonify(strikes), 200

@strike_api.route('', methods=['POST'])
def create_strike():
    data = request.get_json()
    strike = Strike(
        order_number      = data['order_number'],
        sku               = data.get('sku'),
        name              = data.get('name'),  # Include name for item strike
        strike_type       = data['strike_type'],
        missing_quantity  = data.get('missing_quantity', 0),
        detail            = data.get('detail')
    )
    new_id = strike.save()
    order = Order.find_by_order_number(strike.order_number)
    if not order:
        return jsonify({'error': 'Pedido no encontrado'}), 404

    products = order.products or []

    # 3) Modificar o eliminar el producto afectado
    for idx, prod in enumerate(products):
        if prod.get('sku') == strike.sku:
            qty = prod.get('quantity', 0)
            if strike.missing_quantity >= qty:
                # eliminar el producto completo
                products.pop(idx)
            else:
                # sólo restar la cantidad faltante
                prod['quantity'] = qty - strike.missing_quantity
            break

    # 4) Actualizar en la base de datos
    order.products = products
    order.updated()
    ruta = Route.find_by_date(order.delivery_date)
    for stop in ruta.stops:
        if stop["order_number"] == order.order_number:
            stop["total_charged"] = sum(item['price_sale'] * item['quantity'] for item in order.products)
            stop["total_to_charge"] = sum(item['price_sale'] * item['quantity'] for item in order.products)
            stop["quantity_sku"] = len(order.products)
            stop["payment_method"] = order.paymentMethod
            stop["payment_date"] = order.payment_date
            stop["address"] = order.deliveryAddress
            stop["driver_name"] = order.driver_name
    route_exist = Route(
        id=ruta.id,
        route_number=ruta.route_number,
        close_date=ruta.close_date,
        cost=ruta.cost,
        stops=ruta.stops
    )
    route_exist.update()
    return jsonify({'id': new_id}), 201

@strike_api.route('/<string:id>', methods=['GET'])
def get_strike(id):
    doc = Strike.get(id)
    if not doc:
        return jsonify({'message': 'Strike not found'}), 404
    return jsonify(doc), 200

@strike_api.route('/<string:id>', methods=['PUT'])
def update_strike(id):
    data = request.get_json()
    existing = Strike.get(id)
    if not existing:
        return jsonify({'message': 'Strike not found'}), 404

    strike = Strike(
        order_number      = data.get('order_number', existing['order_number']),
        sku               = data.get('sku', existing.get('sku')),
        name              = data.get('name', existing.get('name')),  # Include name for item strike
        strike_type       = data.get('strike_type', existing['strike_type']),
        missing_quantity  = data.get('missing_quantity', existing.get('missing_quantity', 0)),
        detail            = data.get('detail', existing.get('detail')),
        timestamp         = existing.get('timestamp'),
        id                = id
    )
    strike.update()
    return jsonify({'message': 'updated'}), 200

@strike_api.route('/<string:id>', methods=['DELETE'])
def delete_strike(id):
    existing = Strike.get(id)
    if not existing:
        return jsonify({'message': 'Strike not found'}), 404

    strike = Strike(
        order_number      = existing['order_number'],
        sku               = existing.get('sku'),
        strike_type       = existing['strike_type'],
        missing_quantity  = existing.get('missing_quantity', 0),
        detail            = existing.get('detail'),
        timestamp         = existing.get('timestamp'),
        id                = id
    )
    strike.delete()
    return jsonify({'message': 'deleted'}), 200
