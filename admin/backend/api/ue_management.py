from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from babel import numbers
import locale
import json

from ..models.inventory import Inventory
from ..models.purchase import Purchase
from ..models.order import Order
from ..models.route import Route

from ..db import get_db

# Blueprint
ue_api = Blueprint('ue', __name__)
db = get_db()

# Colecciones MongoDB
orders_collection = db['orders']
purchases_collection = db['purchases']
routes_collection = db['routes']
costs_collection = db["costs"]
unit_economics_collection = db['unit_economics']

# Configuración regional (segura)
try:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "es_CO.UTF-8")


# -------------------- Crear registro de unidad económica diaria --------------------
def func_create_ue(fecha_in):
    """
    Calcula métricas diarias de unidad económica y guarda el registro.
    """
    # COGS por pipeline (simplificado)
    pipeline_cog = [
        {"$match": {"delivery_date": fecha_in}},
        {"$unwind": "$products"},
        {"$group": {
            "_id": "$delivery_date",
            "cogs": {"$sum": {"$multiply": ["$products.price_sale", "$products.quantity"]}}
        }}
    ]

    cogs_result = list(orders_collection.aggregate(pipeline_cog))
    cogs = cogs_result[0]["cogs"] if cogs_result else 0

    # Datos auxiliares
    inventario_hoy = Inventory.total_by_date(fecha_in)
    fecha_ayer = (datetime.strptime(fecha_in, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    inventario_ayer = Inventory.total_by_date(fecha_ayer)
    purchase_value = Purchase.total_by_date(fecha_in)

    # Ordenes del día
    clientes = set()
    gmv = 0
    total_ordenes = 0
    total_lineas = 0
    ordenes = orders_collection.find({"delivery_date": fecha_in})

    for orden in ordenes:
        total_ordenes += 1
        clientes.add(orden.get("customer_email", ""))
        for producto in orden.get("products", []):
            cantidad = float(producto.get("quantity", 0))
            precio = float(producto.get("price_sale", 0))
            total_lineas += 1
            gmv += cantidad * precio

    aov = round(gmv / total_ordenes, 2) if total_ordenes > 0 else 0
    alv = round(gmv / total_lineas, 2) if total_lineas > 0 else 0

    # Cartera y métodos de pago
    cartera_total = 0
    efectivo = 0
    davivienda = 0
    bancolombia = 0
    cartera = 0

    orders_with_cartera = Order.find_by_status("Pendiente de pago")
    for order in orders_with_cartera:
        cartera_total += float(order.get("total", 0))

    rutas = Route.find_by_date(fecha_in)
    if rutas:
        for ruta in rutas:
            stops = ruta.get("stops", [])
            for stop in stops:
                total_charged = float(stop.get("total_charged", 0))
                if stop.get("status") == "Pagada":
                    if stop.get("payment_method") == "Davivienda":
                        davivienda += total_charged
                    elif stop.get("payment_method") == "Bancolombia":
                        bancolombia += total_charged
                    elif stop.get("payment_method") == "Efectivo":
                        efectivo += total_charged
                else:
                    cartera += total_charged

    # Cálculos generales
    leakage = purchase_value + inventario_ayer - inventario_hoy - cogs
    margin = round(((gmv - cogs) / gmv * 100), 2) if gmv > 0 else 0
    cash_margin = round(gmv - cogs, 2)

    new_ue = {
        "close_date": fecha_in,
        "gmv": gmv,
        "cogs": cogs,
        "purchase": purchase_value,
        "leakage": leakage,
        "inventory": inventario_hoy,
        "Net Profit": 0,
        "Gross Profit as % of GMV": margin,
        "Gross Profit": cash_margin,
        "orders": total_ordenes,
        "lines": total_lineas,
        "aov": aov,
        "alv": alv,
        "cash_margin": cash_margin,
        "cartera_total": cartera_total,
        "cartera_today": cartera,
        "davivienda": davivienda,
        "bancolombia": bancolombia,
        "cash": efectivo,
    }

    unit_economics_collection.insert_one(new_ue)
    return jsonify({"message": f"Unidad económica del {fecha_in} creada exitosamente"}), 201


# -------------------- Obtener UE por tipo --------------------
@ue_api.route('/ue/<string:tipo>', methods=['GET'])
def get_ue(tipo):
    ue_list = list(unit_economics_collection.find({'tipo': tipo.capitalize()}, {'_id': 0}))
    return jsonify(ue_list), 200


# -------------------- Actualizar métricas mensuales/semanales --------------------
@ue_api.route('/updateUE', methods=['POST'])
def update_ue():
    data = request.get_json()
    fecha_base_str = data.get("dateUpdate")
    if not fecha_base_str:
        return jsonify({"message": "Falta el campo 'dateUpdate'"}), 400

    fecha_base = datetime.strptime(fecha_base_str, "%Y-%m-%d")
    nombre_mes = fecha_base.strftime('%B').capitalize()

    # Costos fijos del mes
    costos = {c['typeCost']: c['amount'] for c in costs_collection.find(
        {"typePeriod": "Mensual", "period": nombre_mes}
    )}

    # Variables de costos
    wh_rent = costos.get("wh_rent", 0)
    cost_tech = costos.get("cost_tech", 0)
    sales_force = costos.get("sales_force", 0)
    cost_others = costos.get("cost_others", 0)
    cost_supply = costos.get("cost_supply", 0)
    personnel = costos.get("personnel", 0)

    # Fechas de referencia
    inicio_mes = fecha_base.replace(day=1)
    fin_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    inicio_semana = fecha_base - timedelta(days=fecha_base.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    periodos = [
        ("Mensual", inicio_mes.strftime('%Y-%m-%d'), fin_mes.strftime('%Y-%m-%d')),
        ("Semanal", inicio_semana.strftime('%Y-%m-%d'), fin_semana.strftime('%Y-%m-%d')),
    ]

    for tipo, fecha_inicio, fecha_fin in periodos:
        gmv, cogs, total_ordenes, total_lineas, clientes = 0, 0, 0, 0, set()
        costo_logistico = 0

        ordenes = orders_collection.find({"delivery_date": {"$gte": fecha_inicio, "$lte": fecha_fin}})
        for orden in ordenes:
            total_ordenes += 1
            clientes.add(orden.get('customer_email', ''))
            for producto in orden.get('products', []):
                gmv += float(producto.get('price_sale', 0)) * float(producto.get('quantity', 0))
                total_lineas += 1

        compras = purchases_collection.find({"date": {"$gte": fecha_inicio, "$lte": fecha_fin}})
        for compra in compras:
            for producto in compra.get('products', []):
                precio = float(producto.get('final_price_purchase', 0))
                cantidad = float(producto.get('total_quantity_ordered', 0))
                cogs += precio * cantidad

        rutas = routes_collection.find({"close_date": {"$gte": fecha_inicio, "$lte": fecha_fin}})
        for ruta in rutas:
            costo_logistico += float(ruta.get('cost', 0))

        # Distribución semanal/mensual
        divisor = 4 if tipo == "Semanal" else 1
        wh_rent_d = wh_rent / divisor
        cost_tech_d = cost_tech / divisor
        sales_force_d = sales_force / divisor
        cost_others_d = cost_others / divisor
        cost_supply_d = cost_supply / divisor
        personnel_d = personnel / divisor

        opex = round(wh_rent_d + cost_tech_d + cost_others_d + cost_supply_d +
                     costo_logistico + personnel_d, 2)
        margen_neto = round(gmv - cogs, 2)
        utilidad_bruta = round(margen_neto - opex - sales_force_d, 2)

        aov = round(gmv / total_ordenes, 2) if total_ordenes > 0 else 0
        alv = round(gmv / total_lineas, 2) if total_lineas > 0 else 0
        mua = len(clientes)

        def formato(valor):
            return numbers.format_currency(valor, 'COP', locale='es_CO') if valor else "$0"

        # Reemplazar datos anteriores
        unit_economics_collection.delete_many({
            "tipo": tipo,
            "periodo": nombre_mes if tipo == "Mensual" else f"Semana {fecha_base.isocalendar()[1]}"
        })

        unit_economics_collection.insert_one({
            "year": fecha_base.year,
            "tipo": tipo,
            "periodo": nombre_mes if tipo == "Mensual" else f"Semana {fecha_base.isocalendar()[1]}",
            "GMV": formato(gmv),
            "COGS": formato(cogs),
            "Last Mile": formato(costo_logistico),
            "WH Rent": formato(wh_rent_d),
            "Tech Cost": formato(cost_tech_d),
            "Sales Force": formato(sales_force_d),
            "Others Cost": formato(cost_others_d),
            "Supply Cost": formato(cost_supply_d),
            "Personnel": formato(personnel_d),
            "Opex": formato(opex),
            "Net Profit": formato(utilidad_bruta),
            "Gross Profit as % of GMV": f"{round((1 - (cogs / gmv)) * 100, 2)}%" if gmv > 0 else "0%",
            "Gross Profit": formato(margen_neto),
            "Orders": total_ordenes,
            "Lines": total_lineas,
            "AOV": formato(aov),
            "ALV": formato(alv),
            "MUA": mua
        })

    return jsonify({"message": "Unidad económica actualizada exitosamente"}), 200
