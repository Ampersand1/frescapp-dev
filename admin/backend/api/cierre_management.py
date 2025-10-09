from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
import time
from bson import json_util

# Modelos
from ..models.cierre import Cierre
from ..models.route import Route
from ..models.inventory import Inventory
from ..models.purchase import Purchase
from ..models.cost import Cost
from ..models.order import Order
from ..models.product import Product
from ..models.product_history import ProductHistory

# APIs relacionadas (se importan dentro de las funciones para evitar ciclos)
# from . import alegra_management, route_management, purchase_management, inventory_management

# Configuración de Flask Blueprint
cierres_api = Blueprint('cierres', __name__)

# --- Función auxiliar para obtener DB dentro del contexto ---
def get_db():
    from ..db import get_db
    return get_db()

# --- Función principal para crear el cierre ---
def func_create_cierre(fecha_in):
    db = get_db()
    orders_collection = db['orders']

    # --- PIPELINE para calcular COGS ---
    pipeline_cog = [
        {"$match": {"delivery_date": {"$gte": fecha_in, "$lte": fecha_in}}},
        {"$unwind": "$products"},
        {"$lookup": {"from": "products", "localField": "products.sku", "foreignField": "sku", "as": "product_info"}},
        {"$unwind": "$product_info"},
        {"$lookup": {"from": "products", "localField": "product_info.child", "foreignField": "sku", "as": "child_product_info"}},
        {"$unwind": {"path": "$child_product_info", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {
            "from": "purchases",
            "let": {"sku": "$child_product_info.sku", "delivery_date": "$delivery_date"},
            "pipeline": [
                {"$unwind": "$products"},
                {"$match": {"$expr": {"$and": [
                    {"$eq": ["$products.sku", "$$sku"]},
                    {"$eq": ["$date", "$$delivery_date"]}
                ]}}}
            ],
            "as": "purchase_info"
        }},
        {"$lookup": {
            "from": "inventory",
            "let": {"sku": "$child_product_info.sku", "delivery_date": "$delivery_date"},
            "pipeline": [
                {"$unwind": "$products"},
                {"$match": {"$expr": {"$and": [
                    {"$eq": ["$products.sku", "$$sku"]},
                    {"$eq": ["$close_date", {
                        "$dateToString": {"format": "%Y-%m-%d", "date": {
                            "$dateSubtract": {"startDate": {"$toDate": "$$delivery_date"}, "unit": "day", "amount": 1}
                        }}
                    }]}
                ]}}}
            ],
            "as": "inventory_info"
        }},
        {"$unwind": {"path": "$purchase_info", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$inventory_info", "preserveNullAndEmptyArrays": True}},
        {"$group": {
            "_id": {"fecha": "$delivery_date", "sku": "$child_product_info.sku"},
            "cantidad_vendida": {"$sum": {"$multiply": ["$products.quantity", "$product_info.step_unit"]}},
            "cantidad_inventario": {"$first": {"$ifNull": ["$inventory_info.products.quantity", 0]}},
            "precio_inventario": {"$first": {"$ifNull": ["$inventory_info.products.cost", 0]}},
            "precio_compra": {"$first": {"$ifNull": ["$purchase_info.products.final_price_purchase", 0]}}
        }},
        {"$addFields": {"costo_total": {
            "$cond": [
                {"$gte": ["$cantidad_inventario", "$cantidad_vendida"]},
                {"$multiply": ["$cantidad_vendida", "$precio_inventario"]},
                {"$add": [
                    {"$multiply": ["$cantidad_inventario", "$precio_inventario"]},
                    {"$multiply": [
                        {"$subtract": ["$cantidad_vendida", "$cantidad_inventario"]},
                        "$precio_compra"
                    ]}
                ]}
            ]
        }}},
        {"$group": {"_id": "$_id.fecha", "cogs": {"$sum": "$costo_total"}}}
    ]

    inventario_hoy = Inventory.total_by_date(fecha_in)
    fecha_ayer = (datetime.strptime(fecha_in, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    inventario_ayer = Inventory.total_by_date(fecha_ayer)
    purchase_value = Purchase.total_by_date(fecha_in)
    cogs_cursor = db.orders.aggregate(pipeline_cog)
    doc = next(cogs_cursor, None)
    cogs = doc['cogs'] if doc else 0

    # --- Calcular métricas principales ---
    gmv = total_lineas = total_ordenes = 0
    clientes = set()
    for orden in orders_collection.find({"delivery_date": fecha_in}):
        total_ordenes += 1
        clientes.add(orden.get('customer_email'))
        for producto in orden.get('products', []):
            total_lineas += 1
            gmv += producto.get('price_sale', 0) * producto.get('quantity', 0)

    aov = round(gmv / total_ordenes, 2) if total_ordenes else 0
    alv = round(gmv / total_lineas, 2) if total_lineas else 0

    # --- Cartera y pagos ---
    cartera_total = sum(int(order.get("total", 0)) for order in Order.find_by_status("Pendiente de pago"))
    efectivo = davivienda = bancolombia = cartera = 0
    ruta = Route.find_by_date(fecha_in)
    cost_log = ruta.cost if ruta else 0
    if ruta:
        for stop in ruta.stops:
            total_charged = int(stop.get("total_charged", 0))
            if stop.get("status") == "Pagada":
                if stop.get("payment_method") == "Efectivo":
                    efectivo += total_charged
                elif stop.get("payment_method") == "Davivienda":
                    davivienda += total_charged
                elif stop.get("payment_method") == "Bancolombia":
                    bancolombia += total_charged
            else:
                cartera += total_charged

    new_ue = {
        "close_date": fecha_in,
        "gmv": gmv,
        "cogs": cogs,
        "purchase": purchase_value,
        "leakage": float(purchase_value) + float(inventario_ayer) - float(inventario_hoy) - float(cogs),
        "inventory": inventario_hoy,
        "Net Profit": 0,
        "Gross Profit as % of GMV": 0,
        "Gross Profit": 0,
        "orders": total_ordenes,
        "lines": total_lineas,
        "aov": aov,
        "alv": alv,
        "cash_margin": round(gmv - cogs, 2),
        "margin": round(((gmv - cogs) / gmv * 100), 2) if gmv > 0 else 0,
        "cartera_total": cartera_total,
        "cartera_today": cartera,
        "davivienda": davivienda,
        "bancolombia": bancolombia,
        "cash": efectivo,
        "cost_log": cost_log,
    }
    db.cierres.insert_one(new_ue)


# === Rutas ===

@cierres_api.route('/', methods=['GET'])
def list_cierres():
    cierres = Cierre.listar()
    return jsonify([
        {**{k: v for k, v in item.items() if k != '_id'}, "id": str(item["_id"])}
        for item in cierres
    ])


@cierres_api.route('/<fecha>/', methods=['GET'])
def get_cierre(fecha):
    try:
        cierre = Cierre.obtener_por_fecha(fecha)
        inventario = Inventory.get_by_date(fecha)
        purchase = Purchase.get_by_date(fecha)
        ruta = Route.find_by_date(fecha)
        return jsonify({
            "cierre": cierre.to_dict() if cierre else None,
            "inventario": inventario.to_dict() if inventario else None,
            "purchase": purchase.to_dict() if purchase else None,
            "ruta": ruta.to_dict() if ruta else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cierres_api.route('/<fecha_in>', methods=['POST'])
def create_cierre(fecha_in):
    # Importes diferidos para evitar ciclos
    from . import alegra_management as alegra_api
    from . import route_management as route_api
    from . import purchase_management as purchase_api
    from . import inventory_management as inventory_api

    # 1. Facturar pedidos
    for order in Order.find_by_date(fecha_in, fecha_in):
        if order.get("alegra_id") == "000":
            alegra_api.func_send_invoice(order["order_number"])
            time.sleep(3)

    # 2. Facturar compras (excepto domingos)
    fecha_obj = datetime.strptime(fecha_in, "%Y-%m-%d")
    if fecha_obj.weekday() != 6:
        purchase = Purchase.get_by_date(fecha_in)
        if purchase and purchase.status != "Facturada":
            alegra_api.func_send_purchase(fecha_in)

    # 3. Crear ruta del día siguiente
    fecha_siguiente = (fecha_obj + timedelta(days=1)).strftime("%Y-%m-%d")
    route_api.func_create_route(fecha_siguiente)

    # 4. Crear compra e inventario del día siguiente
    purchase_api.func_create_purchase(fecha_siguiente)

    if fecha_obj.weekday() == 5:  # sábado
        sabado = fecha_in
        domingo = fecha_siguiente
        inventario_sabado = Inventory.get_by_date(sabado)
        if inventario_sabado:
            nuevo_inventario = Inventory(close_date=domingo, products=inventario_sabado.products)
            nuevo_inventario.save()
    else:
        inventory_api.func_create_inventory(fecha_siguiente)

    # 5. Crear el cierre
    func_create_cierre(fecha_in)
    return jsonify({"message": "Cierre creado exitosamente"}), 201
