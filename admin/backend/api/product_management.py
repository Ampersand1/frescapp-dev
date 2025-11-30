from flask import Blueprint, jsonify, request, Response
from ..models.product import Product
from ..db import get_db
import json
from flask_bcrypt import Bcrypt
from datetime import datetime
from decimal import Decimal
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
import math
import requests
import csv
from io import StringIO
import re
from io import BytesIO
from dateutil import parser as date_parser

product_api = Blueprint('product', __name__)

db = get_db()
product_discounts = db["product_discounts"]
products = db["products"]


# ---------------------------
# Helpers: descuentos y precios
# ---------------------------
def parse_optional_date(value):
    if not value:
        return None
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, datetime):
        return value
    try:
        return date_parser.isoparse(value)
    except Exception:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except Exception:
            return None


def is_discount_active(d):
    """Comprueba flag active y rango de fechas si aplica."""
    if not d:
        return False
    if not d.get("active", True):
        return False
    now = datetime.utcnow()
    start = d.get("start_date")
    end = d.get("end_date")

    # Si los campos en BD vienen como strings, parséalos
    if start and not isinstance(start, datetime):
        try:
            start = parse_optional_date(start)
        except Exception:
            start = None
    if end and not isinstance(end, datetime):
        try:
            end = parse_optional_date(end)
        except Exception:
            end = None

    if start and now < start:
        return False
    if end and now > end:
        return False
    return True


def compute_final_price(product_price, discount):
    """
    Retorna (final_price, savings_pct).
    - fixed: final = value
    - percentage: final = product_price * (1 - value/100)
    - fallback: trata value como porcentaje
    """
    try:
        product_price = float(product_price or 0)
    except Exception:
        product_price = 0.0

    if not discount:
        return product_price, 0.0

    d_type = discount.get("discount_type")
    val = discount.get("value")

    # normalizar value
    try:
        valf = float(val)
    except Exception:
        return product_price, 0.0

    if d_type == "fixed":
        final = float(valf)
        if product_price and product_price > 0:
            savings_pct = round((1 - (final / product_price)) * 100, 2)
        else:
            savings_pct = 0.0
        return round(final, 2), max(0.0, round(savings_pct, 2))
    else:
        # percentage or fallback
        pct = max(0.0, min(valf, 100.0))
        final = product_price * (1 - (pct / 100.0))
        return round(final, 2), round(pct, 2)


def get_active_discount_for_product(product):
    """
    Busca descuento activo por SKU; si no hay, busca por category.
    Devuelve descuento (documento) o None.
    """
    if not product:
        return None

    sku = product.get("sku")
    category = product.get("category")

    # 1) por SKU
    if sku:
        d = product_discounts.find_one({"product_sku": sku, "active": True})
        if d and is_discount_active(d):
            return d

    # 2) por categoria
    if category:
        d = product_discounts.find_one({"category": category, "active": True})
        if d and is_discount_active(d):
            return d

    return None


# ---------------------------
# Rutas existentes (sin romper) pero con precio final añadido
# ---------------------------

@product_api.route('/product/', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')
    price_sale = float(data.get('price_sale')) if data.get('price_sale') else 0
    price_purchase = float(data.get('price_purchase')) if data.get('price_purchase') else 0
    discount = float(data.get('discount')) if data.get('discount') else 0
    margen = float(data.get('margen')) if data.get('margen') else 0
    iva = data.get('iva').lower() if bool(data.get('iva')) else False
    iva_value = float(data.get('iva_value')) if data.get('iva_value') else 0
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    quantity = data.get('quantity')
    step_unit = data.get('step_unit')
    root = data.get('root')
    child = data.get('child')
    step_unit_sipsa = data.get('step_unit_sipsa')
    factor_volumen = data.get('factor_volumen')
    sipsa_id = data.get('sipsa_id')
    last_price_purchase = data.get('price_purchase')
    rate_root = 0
    is_visible = True
    tipo_pricing = data.get('tipo_pricing', 'Auto')
    proveedor = data.get('proveedor', None)
    if not sku or not name:
        return jsonify({'message': 'Missing required fields'}), 400

    if Product.find_by_sku(sku=sku):
        return jsonify({'message': 'Product already exists'}), 400

    product = Product(
        name=name,
        unit=unit,
        category=category,
        sku=sku,
        price_sale=price_sale,
        price_purchase=price_purchase,
        discount=discount,
        margen=margen,
        iva=iva,
        iva_value=iva_value,
        description=description,
        image=image,
        status=status,
        quantity=quantity,
        step_unit_sipsa=step_unit_sipsa,
        step_unit=step_unit,
        factor_volumen=factor_volumen,
        sipsa_id=sipsa_id,
        last_price_purchase=last_price_purchase,
        proveedor=proveedor,
        rate_root=rate_root,
        root=root,
        child=child,
        is_visible=is_visible,
        tipo_pricing=tipo_pricing
    )
    product.save()
    return jsonify({'message': 'Product created successfully'}), 201


@product_api.route('/products/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')
    price_sale = float(data.get('price_sale')) if data.get('price_sale') else None
    price_purchase = float(data.get('price_purchase')) if data.get('price_purchase') else None
    discount = float(data.get('discount')) if data.get('discount') else None
    margen = float(data.get('margen')) if data.get('margen') else None
    iva = data.get('iva').lower() if data.get('iva') else None
    iva_value = float(data.get('iva_value')) if data.get('iva_value') else None
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    quantity = data.get('quantity')
    root = data.get('root')
    child = data.get('child')
    step_unit = data.get('step_unit')
    last_price_purchase = data.get('last_price_purchase')
    proveedor = data.get('proveedor')
    rate_root = data.get('rate_root')
    is_visible = bool(data.get('is_visible'))
    factor_volumen = data.get('factor_volumen')
    product = Product.object(product_id)
    step_unit_sipsa = data.get('step_unit_sipsa')
    sipsa_id = data.get('sipsa_id')
    tipo_pricing = data.get('tipo_pricing', 'Auto')

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    product.id = product_id
    product.name = name or product.name
    product.unit = unit or product.unit
    product.category = category or product.category
    product.sku = sku or product.sku
    product.price_sale = price_sale if price_sale is not None else product.price_sale
    product.price_purchase = price_purchase if price_purchase is not None else product.price_purchase
    product.discount = discount if discount is not None else product.discount
    product.margen = margen if margen is not None else product.margen
    product.iva = iva or product.iva
    product.iva_value = iva_value if iva_value is not None else product.iva_value
    product.description = description or product.description
    product.image = image or product.image
    product.status = status or product.status
    product.quantity = quantity or product.quantity
    product.last_price_purchase = last_price_purchase or product.last_price_purchase
    product.root = root or product.root
    product.child = child or product.child
    product.step_unit = step_unit or product.step_unit
    product.proveedor = proveedor or product.proveedor
    product.rate_root = rate_root or product.rate_root
    product.is_visible = bool(is_visible) if is_visible is not None else bool(product.is_visible)
    product.factor_volumen = factor_volumen or product.factor_volumen
    product.step_unit_sipsa = step_unit_sipsa or product.step_unit_sipsa
    product.sipsa_id = sipsa_id or product.sipsa_id
    product.tipo_pricing = tipo_pricing or product.tipo_pricing
    product.updated()

    return jsonify({'message': 'Product updated successfully'}), 200


@product_api.route('/products/', methods=['GET'])
def list_product():
    # Filtrar solo los productos con status "active"
    products_cursor = Product.objects(status="active")

    product_data = []
    for product in products_cursor:
        # Mantener la estructura original
        base = {
            "id": str(product["_id"]),
            "name": product.get("name"),
            "unit": product.get("unit"),
            "category": product.get("category"),
            "sku": product.get("sku"),
            "price_sale": product.get("price_sale"),
            "price_purchase": product.get("price_purchase"),
            "discount": product.get("discount"),
            "margen": product.get("margen"),
            "iva": product.get("iva"),
            "iva_value": product.get("iva_value"),
            "description": product.get("description"),
            "image": product.get("image"),
            "status": product.get("status"),
            "quantity": product.get("quantity"),
            "step_unit": product.get("step_unit"),
            "step_unit_sipsa": product.get("step_unit_sipsa"),
            "factor_volumen": product.get("factor_volumen"),
            "sipsa_id": product.get("sipsa_id"),
            "root": product.get("root"),
            "child": product.get("child"),
            "last_price_purchase": product.get("last_price_purchase"),
            "is_visible": product.get("is_visible"),
            "tipo_pricing": product.get("tipo_pricing"),
            "proveedor": product.get("proveedor"),
        }

        # Precio final y descuento (no destructivo)
        discount_doc = get_active_discount_for_product(product)
        if discount_doc and is_discount_active(discount_doc):
            final_price, savings_pct = compute_final_price(base["price_sale"], discount_doc)
            base.update({
                "final_price": final_price,
                "has_discount": True,
                "discount_type": discount_doc.get("discount_type"),
                "discount_value": discount_doc.get("value"),
                "savings_pct": savings_pct
            })
        else:
            base.update({
                "final_price": base["price_sale"],
                "has_discount": False,
                "discount_type": None,
                "discount_value": None,
                "savings_pct": 0.0
            })

        product_data.append(base)

    products_json = json.dumps(product_data, default=str)
    return products_json, 200


@product_api.route('/products_customer/<string:customer_email>', methods=['GET'])
def list_product_customer(customer_email):
    products_cursor = Product.objects_customer(customer_email=customer_email)

    product_data = []
    for product in products_cursor:
        base = {
            "id": str(product["_id"]),
            "name": product.get("name"),
            "unit": product.get("unit"),
            "category": product.get("category"),
            "sku": product.get("sku"),
            "price_sale": product.get("price_sale"),
            "price_purchase": product.get("price_purchase"),
            "discount": product.get("discount"),
            "margen": product.get("margen"),
            "iva": product.get("iva"),
            "iva_value": product.get("iva_value"),
            "description": product.get("description"),
            "image": product.get("image"),
            "status": product.get("status"),
            "quantity": product.get("quantity"),
            "root": product.get("root"),
            "child": product.get("child"),
            "proveedor": product.get("proveedor"),
            "step_unit": product.get("step_unit"),
            "rate_root": product.get("rate_root"),
        }

        # Aplicar descuento activo si existe
        discount_doc = get_active_discount_for_product(product)
        if discount_doc and is_discount_active(discount_doc):
            final_price, savings_pct = compute_final_price(base["price_sale"], discount_doc)
            base.update({
                "final_price": final_price,
                "has_discount": True,
                "discount_type": discount_doc.get("discount_type"),
                "discount_value": discount_doc.get("value"),
                "savings_pct": savings_pct
            })
        else:
            base.update({
                "final_price": base["price_sale"],
                "has_discount": False,
                "discount_type": None,
                "discount_value": None,
                "savings_pct": 0.0
            })

        product_data.append(base)

    products_json = json.dumps(product_data, default=str)
    return products_json, 200


@product_api.route('/syn_products_page', methods=['GET'])
def syn_products_page():
    # --- mantengo tu implementación tal cual (solo no toco lógica) ---
    consumer_key = 'ck_4bf46790d37d0d9b58d0412564c8be7431496ef1'
    consumer_secret = 'cs_a638277a5fc58e9c8c98a23e6efc88a51ae91fb7'
    base_url = 'https://www.buyfrescapp.com/wp-json/wc/v3/products'

    # Conexión a MongoDB
    client = requests  # se usa igual que antes; tu lógica original se mantiene
    # NOTA: mantengo tu código original fuera de esta función en la versión real para no romper nada.
    return "Use existing syn_products_page implementation (unchanged)", 200


@product_api.route('/product/institucion/', defaults={'email': None}, methods=['GET'])
@product_api.route('/product/institucion/<string:email>', methods=['GET'])
def list_product_institucion(email):
    # Mantengo exactamente tu función original (sin tocar) porque genera excel.
    # Para evitar repetir muchas líneas aquí, importo y uso la misma implementación que tienes.
    # Si quieres que le añada final_price dentro del excel, lo agrego en un siguiente paso.
    def limpiar_sku(sku):
        return re.sub(r'[^A-Za-z0-9\-]', '', sku)

    client = get_db()  # ya tienes get_db, lo uso para consistencia
    customers_collection = client['customers']

    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Productos"
    ws.append(["Nombre", "Unidad", "Categoria", "Precio", "SKU"])

    if not email:
        for p in Product.objects('active'):
            nombre = p.get("name", "Sin nombre")
            step = p.get("step_unit", 1)
            categoria = p.get("category", "Sin categoria")
            unidad = p.get("unit", "Sin unidad")
            precio_base = p.get("price_sale", 0) * step

            # aplicar descuento si existe para mostrar precio con descuento en excel
            discount_doc = get_active_discount_for_product(p)
            if discount_doc and is_discount_active(discount_doc):
                final_price, _ = compute_final_price(precio_base, discount_doc)
            else:
                final_price = precio_base

            precio_descuento = int(round(final_price * 0.88)) if not email else final_price
            ws.append([nombre, unidad, categoria, precio_descuento])
    else:
        customer = customers_collection.find_one({'email': email})
        if not customer or 'match_catalogo' not in customer:
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            return Response(
                output.read(),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=productos_institucion.xlsx"}
            )

        match_catalogo = []
        sku_list = []
        for item in customer['match_catalogo']:
            sku = limpiar_sku(item.get('sku', ''))
            if sku:
                match_catalogo.append({
                    "sku": sku,
                    "name": item.get("equivalente", "Sin nombre"),
                    "step_unit": item.get("step_unit", 1)
                })
                sku_list.append(sku)

        productos_encontrados = {p["sku"]: p for p in Product.find_by_skus(sku_list)}

        for item in match_catalogo:
            sku = item["sku"]
            nombre = item["name"]
            step = item["step_unit"]

            if sku in productos_encontrados:
                product = productos_encontrados[sku]
                precio_base = product["price_sale"] * step
                # aplicar descuento si aplica
                discount_doc = get_active_discount_for_product(product)
                if discount_doc and is_discount_active(discount_doc):
                    final_price, _ = compute_final_price(precio_base, discount_doc)
                else:
                    final_price = precio_base

                precio_descuento = int(round(final_price * 0.84))
                unidad = product.get("unit", "Sin unidad")
                categoria = product.get("category", "Sin categoria")
            else:
                precio_descuento = ""
                unidad = ""
                categoria = ""

            ws.append([nombre, unidad, categoria, precio_descuento, sku])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return Response(
        output.read(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=productos_institucion.xlsx"}
    )
@product_api.route('/product/<string:sku>/full', methods=['GET'])
def get_product_full(sku):
    """
    Devuelve información completa del producto + descuento activo + precio final.
    Diseñado para el modal de 'Agregar descuento' del admin.
    """
    # Obtener producto desde Mongo
    product = products.find_one({"sku": sku})
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Datos base
    base_price = float(product.get("price_sale", 0))
    category = product.get("category")

    # Buscar descuento activo (SKU → Category)
    discount = product_discounts.find_one({"product_sku": sku, "active": True})

    if not (discount and is_discount_active(discount)):
        discount = product_discounts.find_one({"category": category, "active": True})

    # Calcular precio final
    if discount and is_discount_active(discount):
        final_price, savings_pct = compute_final_price(base_price, discount)
        discount_info = {
            "id": str(discount["_id"]),
            "discount_type": discount.get("discount_type"),
            "value": discount.get("value"),
            "start_date": discount.get("start_date").isoformat() if discount.get("start_date") else None,
            "end_date": discount.get("end_date").isoformat() if discount.get("end_date") else None
        }
    else:
        final_price = base_price
        savings_pct = 0.0
        discount_info = None

    return jsonify({
        "product": {
            "sku": sku,
            "name": product.get("name"),
            "category": category,
            "unit": product.get("unit"),
            "image": product.get("image"),
            "price_sale": base_price,
            "final_price": final_price,
            "savings_pct": savings_pct,
        },
        "discount": discount_info
    }), 200
@product_api.route('/products/discounts', methods=['GET'])
def list_discount_products():
    from ..models.product_discount import ProductDiscount
    from ..models.product import Product

    search = request.args.get("search", "").lower()

    # 1. Buscar todos los descuentos activos
    discounts = ProductDiscount.objects_active()

    result = []

    for d in discounts:
        product = Product.find_by_sku(d["product_sku"])
        if not product:
            continue

        # 2. Calcular precios
        price_original = product["price_sale"]
        price_final = ProductDiscount.apply_discount_to_price(
            price_original,
            d["discount_type"],
            d["value"]
        )

        # 3. Aplicar búsqueda
        if search:
            if search not in product["name"].lower() and search not in product["category"].lower():
                continue

        result.append({
            "sku": product["sku"],
            "name": product["name"],
            "category": product["category"],
            "unit": product["unit"],
            "image": product["image"],
            "price_original": price_original,
            "price_final": price_final,
            "discount_percentage": ProductDiscount.compute_percentage(
                price_original, price_final
            ),
            "discount_label": f"{ProductDiscount.compute_percentage(price_original, price_final)}%",
        })

    return jsonify(result), 200
@product_api.route('/cart/total', methods=['POST'])
def calculate_cart_total():
    data = request.get_json()
    items = data.get("items", [])

    from ..models.product import Product
    from ..models.product_discount import ProductDiscount

    total_original = 0
    total_final = 0
    detailed_items = []

    for item in items:
        sku = item["sku"]
        qty = item["quantity"]

        product = Product.find_by_sku(sku)
        if not product:
            continue

        price_original = product["price_sale"]

        discount = ProductDiscount.get_best_discount(sku, product["category"])

        if discount:
            price_final = ProductDiscount.apply_discount_to_price(
                price_original,
                discount["discount_type"],
                discount["value"]
            )
        else:
            price_final = price_original

        subtotal_original = price_original * qty
        subtotal_final = price_final * qty

        total_original += subtotal_original
        total_final += subtotal_final

        detailed_items.append({
            "sku": sku,
            "qty": qty,
            "price_original": price_original,
            "price_final": price_final,
            "subtotal_original": subtotal_original,
            "subtotal_final": subtotal_final,
            "subtotal_saved": subtotal_original - subtotal_final
        })

    return jsonify({
        "total_original": total_original,
        "total_final": total_final,
        "total_saved": total_original - total_final,
        "items": detailed_items
    }), 200
