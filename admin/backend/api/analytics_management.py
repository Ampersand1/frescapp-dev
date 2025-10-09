from flask import Blueprint, jsonify, current_app
from datetime import datetime, timedelta
import json
from bson import json_util
from ..models.order import Order
from ..models.product import Product
from ..db import get_db  


analytics_api = Blueprint('analytics', __name__)


@analytics_api.route('/health')
def health_check():
    return "OK", 200


# ===========================================
# COSTOS DIARIOS
# ===========================================
@analytics_api.route('/costs', methods=['GET'])
def get_cost():
    from flask import current_app
    with current_app.app_context():
        db = get_db()
        routes_collection = db['routes']
        purchases_collection = db['purchases']
        orders_collection = db['orders']
        costs_collection = db['costs']
        inventory_collection = db['inventory']

        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=120)

        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

        daily_summary = {}

        def initialize_daily_summary(fecha):
            if fecha not in daily_summary:
                daily_summary[fecha] = {
                    "date": fecha,
                    "logistics_cost": 0,
                    "cogs": 0,
                    "gmv": 0,
                    "total_orders": 0,
                    "total_lines": 0,
                    "cost_tech": 6250,
                    "cost_others": 0,
                    "wh_rent": 52080
                }

        # =============== PIPELINE COGS ===============
        pipeline = [
            {"$match": {"delivery_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}}},
            {"$unwind": "$products"},
            {"$lookup": {"from": "products", "localField": "products.sku", "foreignField": "sku", "as": "product_info"}},
            {"$unwind": "$product_info"},
            {"$lookup": {"from": "products", "localField": "product_info.child", "foreignField": "sku", "as": "child_product_info"}},
            {"$unwind": {"path": "$child_product_info", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "purchases",
                    "let": {"sku": "$child_product_info.sku", "delivery_date": "$delivery_date"},
                    "pipeline": [
                        {"$unwind": "$products"},
                        {"$match": {"$expr": {"$and": [{"$eq": ["$products.sku", "$$sku"]}, {"$eq": ["$date", "$$delivery_date"]}]}}}
                    ],
                    "as": "purchase_info"
                }
            },
            {
                "$lookup": {
                    "from": "inventory",
                    "let": {"sku": "$child_product_info.sku", "delivery_date": "$delivery_date"},
                    "pipeline": [
                        {"$unwind": "$products"},
                        {"$match": {"$expr": {"$and": [
                            {"$eq": ["$products.sku", "$$sku"]},
                            {"$eq": ["$close_date", {"$dateToString": {"format": "%Y-%m-%d", "date": {"$dateSubtract": {"startDate": {"$toDate": "$$delivery_date"}, "unit": "day", "amount": 1}}}}]}
                        ]}}}
                    ],
                    "as": "inventory_info"
                }
            },
            {"$unwind": {"path": "$purchase_info", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$inventory_info", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": {"fecha": "$delivery_date", "sku": "$child_product_info.sku"},
                "cantidad_vendida": {"$sum": {"$multiply": ["$products.quantity", "$product_info.step_unit"]}},
                "cantidad_inventario": {"$first": {"$ifNull": ["$inventory_info.products.quantity", 0]}},
                "precio_inventario": {"$first": {"$ifNull": ["$inventory_info.products.cost", 0]}},
                "precio_compra": {"$first": {"$ifNull": ["$purchase_info.products.final_price_purchase", "$product_info.price_purchase"]}}
            }},
            {"$addFields": {
                "costo_total": {
                    "$cond": [
                        {"$gte": ["$cantidad_inventario", "$cantidad_vendida"]},
                        {"$multiply": ["$cantidad_vendida", "$precio_inventario"]},
                        {
                            "$add": [
                                {"$multiply": ["$cantidad_inventario", "$precio_inventario"]},
                                {"$multiply": [{"$subtract": ["$cantidad_vendida", "$cantidad_inventario"]}, "$precio_compra"]}
                            ]
                        }
                    ]
                }
            }},
            {"$group": {"_id": "$_id.fecha", "cogs": {"$sum": "$costo_total"}}}
        ]

        cogs_por_dia = orders_collection.aggregate(pipeline)

        for item in cogs_por_dia:
            fecha = item["_id"]
            initialize_daily_summary(fecha)
            daily_summary[fecha]["cogs"] += item["cogs"]

        # ===== COSTOS LOGÍSTICOS =====
        rutas = routes_collection.find({"close_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}})
        for ruta in rutas:
            fecha = ruta.get('close_date')
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            initialize_daily_summary(fecha)
            daily_summary[fecha]["logistics_cost"] += ruta.get('cost', 0)

        # ===== ORDENES Y GMV =====
        ordenes = orders_collection.find({"delivery_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}})
        for orden in ordenes:
            fecha = orden.get('delivery_date')
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            initialize_daily_summary(fecha)
            daily_summary[fecha]["total_orders"] += 1
            for producto in orden.get('products', []):
                daily_summary[fecha]["total_lines"] += 1
                daily_summary[fecha]["gmv"] += producto.get('price_sale', 0) * producto.get('quantity', 0)

        # ===== COSTOS ADICIONALES =====
        costs = costs_collection.find({"typePeriod": "Diario"})
        for cost in costs:
            fecha = cost.get('period')
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            initialize_daily_summary(fecha)
            tipo_costo = cost.get('typeCost')
            if tipo_costo in daily_summary[fecha]:
                daily_summary[fecha][tipo_costo] += cost.get('amount', 0)

        # ===== RESULTADO FINAL =====
        result = []
        for fecha, data in daily_summary.items():
            for var in ["wh_rent", "logistics_cost", "cogs", "gmv", "total_orders", "total_lines", "cost_tech", "cost_others"]:
                result.append({
                    "fecha": fecha,
                    "variable": var,
                    "valor": float(data[var]) if isinstance(data[var], (int, float)) else 0
                })

        return jsonify(result), 200


# ===========================================
# ÓRDENES Y PRODUCTOS CONSOLIDADOS
# ===========================================
@analytics_api.route('/orders', methods=['GET'])
def get_orders():
    with current_app.app_context():
        db = get_db()
        orders_collection = db['orders']

        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=120)
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

        pipeline = [
            {"$match": {"delivery_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}}},
            {"$unwind": "$products"},
            {"$lookup": {"from": "products", "localField": "products.child", "foreignField": "sku", "as": "product_info"}},
            {"$unwind": "$product_info"},
            {"$project": {
                "order_number": 1,
                "delivery_date": 1,
                "status": 1,
                "products": 1,
                "product_info": 1
            }}
        ]

        orders_data = list(orders_collection.aggregate(pipeline))
        return jsonify(json.loads(json_util.dumps(orders_data))), 200
