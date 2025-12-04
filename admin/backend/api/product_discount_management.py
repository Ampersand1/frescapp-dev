# product_discount_api.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from dateutil import parser as date_parser
from ..db import get_db
from flask_jwt_extended import jwt_required, get_jwt_identity
import math

db = get_db()
product_discounts = db["product_discounts"]
products = db["products"]

product_discount_api = Blueprint("product_discount_api", __name__)

# ---------------------------
# Helpers
# ---------------------------
def serialize_discount(d):
    if not d:
        return None
    return {
        "id": str(d.get("_id")),
        "product_sku": d.get("product_sku"),
        "category": d.get("category"),
        "discount_type": d.get("discount_type"),
        "value": d.get("value"),
        "active": bool(d.get("active", True)),
        "start_date": d.get("start_date").isoformat() if d.get("start_date") else None,
        "end_date": d.get("end_date").isoformat() if d.get("end_date") else None,
        "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
        "updated_at": d.get("updated_at").isoformat() if d.get("updated_at") else None,
    }

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
    if not d:
        return False
    if not d.get("active", True):
        return False
    now = datetime.utcnow()
    start = d.get("start_date")
    end = d.get("end_date")
    if start and now < start:
        return False
    if end and now > end:
        return False
    return True

def compute_final_price(product_price, discount):
    """
    Devuelve (final_price, savings_pct)
    savings_pct es porcentaje (0–100)
    """
    if discount is None:
        return product_price, 0.0

    d_type = discount.get("discount_type")
    val = discount.get("value")

    # Normalización segura del valor
    try:
        val = float(val)
    except:
        return product_price, 0.0

    if val <= 0:
        return product_price, 0.0

    # ----------------------------
    # FIX PARA PRECIO FINAL (fixed)
    # ----------------------------
    if d_type == "fixed":
        # No permitir precios finales mayores al original o negativos
        if val > product_price:
            final = product_price
            savings_pct = 0.0
        else:
            final = max(0.0, val)
            savings_pct = (1 - final / product_price) * 100 if product_price > 0 else 0.0

        final = round(final, 2)
        savings_pct = round(max(0.0, min(savings_pct, 100.0)), 2)
        return final, savings_pct

    # ----------------------------
    # FIX PARA PORCENTAJE (percentage)
    # ----------------------------
    if d_type == "percentage":
        pct = max(0.0, min(val, 100.0))  # limitar 0-100
        final = product_price * (1 - pct / 100.0)
        return round(final, 2), round(pct, 2)

    # fallback seguro
    return round(product_price, 2), 0.0


def require_admin_identity():
    try:
        user = get_jwt_identity() or {}
    except Exception:
        return False, "Invalid token or identity"
    if isinstance(user, dict):
        if user.get("role") == "admin" or user.get("is_admin") == True:
            return True, user
    return False, "Unauthorized: admin role required"

def _dates_overlap(a_start, a_end, b_start, b_end):
    if a_end and b_start and a_end < b_start:
        return False
    if b_end and a_start and b_end < a_start:
        return False
    return True

def _check_conflict(field_name, field_value, start_date, end_date, exclude_id=None):
    query = {field_name: field_value, "active": True}
    if exclude_id:
        try:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        except Exception:
            pass

    candidates = list(product_discounts.find(query))
    for c in candidates:
        c_start = c.get("start_date")
        c_end = c.get("end_date")
        if _dates_overlap(c_start, c_end, start_date, end_date):
            return True, c
    return False, None

def _find_applicable_discount_for_product(product_doc):
    sku = product_doc.get("sku")
    category = product_doc.get("category")

    d = product_discounts.find_one({"product_sku": sku, "active": True})
    if d and is_discount_active(d):
        return d, "sku"

    d = product_discounts.find_one({"category": category, "active": True})
    if d and is_discount_active(d):
        return d, "category"

    return None, None
# ---------------------------
# Routes
# ---------------------------

@product_discount_api.route("/create", methods=["POST"])
#@jwt_required()
def create_product_discount():
    #ok, user_or_msg = require_admin_identity()
    #if not ok:
    #    return jsonify({"error": user_or_msg}), 403

    data = request.get_json() or {}
    product_sku = data.get("product_sku")
    discount_type = data.get("discount_type")
    value = data.get("value")
    active = data.get("active", True)
    start_date = parse_optional_date(data.get("start_date"))
    end_date = parse_optional_date(data.get("end_date"))
    discount_category = data.get("category")

    # Required: either sku or category
    if not product_sku and not discount_category:
        return jsonify({"error": "Debe especificar product_sku o category"}), 400
    if product_sku and discount_category:
        return jsonify({"error": "No puede enviar product_sku y category al mismo tiempo"}), 400

    # discount_type validation
    if discount_type not in ("percentage", "fixed"):
        return jsonify({"error": "discount_type debe ser 'percentage' o 'fixed'"}), 400

    # value numeric and positive & bounds for percentage
    try:
        value = float(value)
    except Exception:
        return jsonify({"error": "value debe ser numérico"}), 400
    if value <= 0:
        return jsonify({"error": "value debe ser mayor a 0"}), 400
    if discount_type == "percentage" and (value < 0 or value > 100):
        return jsonify({"error": "percentage debe estar entre 0 y 100"}), 400

    # Validate existence of referenced product/category
    prod = None
    if product_sku:
        prod = products.find_one({"sku": product_sku})
        if not prod:
            return jsonify({"error": "El SKU no existe en productos"}), 404

        if not discount_category:
            discount_category = prod.get("category")

    if discount_category:
        exists = products.find_one({"category": discount_category})
        if not exists:
            return jsonify({"error": "La categoría no existe en productos"}), 404

    # Validate date logic (start <= end)
    if start_date and end_date and start_date > end_date:
        return jsonify({"error": "start_date no puede ser mayor que end_date"}), 400

    # Conflict detection (no solapamiento permitido para misma SKU o misma categoría)
    if product_sku:
        conflict, existing = _check_conflict("product_sku", product_sku, start_date, end_date)
        if conflict:
            return jsonify({
                "error": "Ya existe un descuento activo/solapado para este SKU",
                "existing_discount": serialize_discount(existing)
            }), 409

    if discount_category and not product_sku:
        # SOLO si el descuento es exclusivamente por categoría
        conflict, existing = _check_conflict("category", discount_category, start_date, end_date)
        if conflict:
            return jsonify({
                "error": "Ya existe un descuento activo/solapado para esta categoría",
                "existing_discount": serialize_discount(existing)
            }), 409

    now = datetime.utcnow()
    doc = {
        "product_sku": product_sku,
        "category": discount_category,
        "discount_type": discount_type,
        "value": value,
        "active": bool(active),
        "start_date": start_date,
        "end_date": end_date,
        "created_at": now,
        "updated_at": now
    }
    res = product_discounts.insert_one(doc)
    doc["_id"] = res.inserted_id

    # Build response showing current product price if SKU was provided
    product_info = None
    if prod:
        original_price = float(prod.get("price_sale", 0))
        final_price, savings_pct = compute_final_price(original_price, doc)
        product_info = {
            "sku": product_sku,
            "original_price": original_price,
            "final_price": final_price,
            "savings_pct": savings_pct
        }

    return jsonify({
        "message": "Discount created",
        "discount": serialize_discount(doc),
        "product": product_info
    }), 201


@product_discount_api.route("/update/<string:discount_id>", methods=["PUT"])
#@jwt_required()
def update_product_discount(discount_id):
    #ok, user_or_msg = require_admin_identity()
    #if not ok:
    #    return jsonify({"error": user_or_msg}), 403

    discount = product_discounts.find_one({"_id": ObjectId(discount_id)})
    if not discount:
        return jsonify({"error": "discount not found"}), 404

    data = request.get_json() or {}
    update = {}

    # Values before update
    new_product_sku = discount.get("product_sku")
    new_category = discount.get("category")
    new_start = discount.get("start_date")
    new_end = discount.get("end_date")
    new_discount_type = discount.get("discount_type")
    new_value = discount.get("value")
    new_active = discount.get("active", True)

    # Update SKU
    if "product_sku" in data:
        new_product_sku = data.get("product_sku")
        new_category = None  # exclusividad

        if new_product_sku:
            prod = products.find_one({"sku": new_product_sku})
            if not prod:
                return jsonify({"error": "El SKU no existe en productos"}), 404
            new_category = prod.get("category")
            update["category"] = new_category
            update["product_sku"] = new_product_sku

    # Update category directly
    if "category" in data:
        new_category = data.get("category")
        new_product_sku = None  # exclusividad
        exists = products.find_one({"category": new_category})
        if not exists:
            return jsonify({"error": "La categoría no existe en productos"}), 404
        update["category"] = new_category
        update["product_sku"] = None

    if "discount_type" in data:
        if data["discount_type"] not in ("percentage", "fixed"):
            return jsonify({"error": "invalid discount_type"}), 400
        new_discount_type = data["discount_type"]
        update["discount_type"] = new_discount_type

    if "value" in data:
        try:
            val = float(data["value"])
            if new_discount_type == "percentage" and (val < 0 or val > 100):
                return jsonify({"error": "percentage must be between 0 and 100"}), 400
            new_value = val
            update["value"] = new_value
        except Exception:
            return jsonify({"error": "value must be numeric"}), 400

    if "active" in data:
        new_active = bool(data["active"])
        update["active"] = new_active

    if "start_date" in data:
        parsed = parse_optional_date(data.get("start_date"))
        if not parsed and data.get("start_date") is not None:
            return jsonify({"error": "invalid start_date"}), 400
        new_start = parsed
        update["start_date"] = new_start

    if "end_date" in data:
        parsed = parse_optional_date(data.get("end_date"))
        if not parsed and data.get("end_date") is not None:
            return jsonify({"error": "invalid end_date"}), 400
        new_end = parsed
        update["end_date"] = new_end

    # Validation
    if new_start and new_end and new_start > new_end:
        return jsonify({"error": "start_date must be before end_date"}), 400

    # Conflict detection
    if new_product_sku:
        conflict, existing = _check_conflict("product_sku", new_product_sku, new_start, new_end, exclude_id=discount_id)
        if conflict:
            return jsonify({
                "error": "Ya existe un descuento activo/solapado para este SKU",
                "existing_discount": serialize_discount(existing)
            }), 409

    if new_category and not new_product_sku:
        conflict, existing = _check_conflict("category", new_category, new_start, new_end, exclude_id=discount_id)
        if conflict:
            return jsonify({
                "error": "Ya existe un descuento activo/solapado para esta categoría",
                "existing_discount": serialize_discount(existing)
            }), 409

    update["updated_at"] = datetime.utcnow()
    product_discounts.update_one({"_id": ObjectId(discount_id)}, {"$set": update})

    updated = product_discounts.find_one({"_id": ObjectId(discount_id)})
    return jsonify({"message": "discount updated", "discount": serialize_discount(updated)}), 200

@product_discount_api.route("/delete/<string:discount_id>", methods=["DELETE"])
#@jwt_required()
def delete_product_discount(discount_id):
    #ok, user_or_msg = require_admin_identity()
    #if not ok:
     #   return jsonify({"error": user_or_msg}), 403

    discount = product_discounts.find_one({"_id": ObjectId(discount_id)})
    if not discount:
        return jsonify({"error": "discount not found"}), 404

    product_discounts.update_one({"_id": ObjectId(discount_id)}, {"$set": {"active": False, "updated_at": datetime.utcnow()}})
    return jsonify({"message": "discount disabled"}), 200

@product_discount_api.route("/all", methods=["GET"])
#@jwt_required()
def get_all_discounts():
    #ok, user_or_msg = require_admin_identity()
    #if not ok:
    #    return jsonify({"error": user_or_msg}), 403

    docs = list(product_discounts.find().sort([("created_at", -1)]))
    serialized = [serialize_discount(d) for d in docs]
    return jsonify(serialized), 200

@product_discount_api.route("/sku/<string:product_sku>", methods=["GET"])
def get_discount_by_sku(product_sku):
    prod = products.find_one({"sku": product_sku})
    if not prod:
        return jsonify({"error": "product not found"}), 404

    category = prod.get("category")
    original_price = float(prod.get("price_sale", 0))

    # 1. Buscar descuento directo por producto
    discount = product_discounts.find_one({"product_sku": product_sku, "active": True})
    if not (discount and is_discount_active(discount)):
        # 2. Si no hay, buscar descuento por categoría
        discount = product_discounts.find_one({"category": category, "active": True})

    if discount and is_discount_active(discount):
        final_price, savings_pct = compute_final_price(original_price, discount)
        origin = "sku" if discount.get("product_sku") else "category"
        return jsonify({
            "discount": serialize_discount(discount),
            "product": {
                "sku": product_sku,
                "category": category,
                "original_price": original_price,
                "final_price": final_price,
                "savings_pct": savings_pct,
                "has_discount": True,
                "discount_origin": origin,
                "discount_id": str(discount.get("_id"))
            }
        }), 200

    return jsonify({
        "message": "No active discount",
        "product": {
            "sku": product_sku,
            "category": category,
            "original_price": original_price,
            "final_price": original_price,
            "savings_pct": 0.0,
            "has_discount": False,
            "discount_origin": None,
            "discount_id": None
        }
    }), 200

@product_discount_api.route("/category/<string:category>", methods=["GET"])
def get_discount_by_category(category):
    discount = product_discounts.find_one({"category": category, "active": True})
    if discount and is_discount_active(discount):
        return jsonify(serialize_discount(discount)), 200
    return jsonify({"message": "No active discount for this category"}), 200

@product_discount_api.route("/apply", methods=["POST"])
def apply_discount_to_product():
    """
    Endpoint público para calcular precio final de un SKU sin crear ni modificar nada en BD.
    Payload:
    {
      "product_sku": "SKU123"
    }
    """
    data = request.get_json() or {}
    product_sku = data.get("product_sku")
    if not product_sku:
        return jsonify({"error": "product_sku required"}), 400

    prod = products.find_one({"sku": product_sku, "status": {"$in": ["active", None]}})
    if not prod:
        return jsonify({"error": "product not found"}), 404

    original_price = float(prod.get("price_sale", 0))

    # buscar descuento activo (prioridad SKU > category)
    discount = product_discounts.find_one({"product_sku": product_sku, "active": True})
    if not (discount and is_discount_active(discount)):
        discount = product_discounts.find_one({"category": prod.get("category"), "active": True})

    if discount and is_discount_active(discount):
        final_price, savings_pct = compute_final_price(original_price, discount)
        origin = "sku" if discount.get("product_sku") else "category"
        return jsonify({
            "sku": product_sku,
            "original_price": original_price,
            "final_price": final_price,
            "savings_pct": savings_pct,
            "has_discount": True,
            "discount_origin": origin,
            "discount": serialize_discount(discount)
        }), 200

    return jsonify({
        "sku": product_sku,
        "original_price": original_price,
        "final_price": original_price,
        "savings_pct": 0.0,
        "has_discount": False,
        "discount": None
    }), 200

@product_discount_api.route("/validate/<string:product_sku>", methods=["GET"])
#@jwt_required()
def validate_discount_possible(product_sku):
    """
    Endpoint que utiliza el módulo productos para consultar:
    - Si ya existe un descuento activo por SKU
    - Si existe un descuento activo por categoría
    - Permite al admin saber si puede crear un nuevo descuento o si hay conflicto.
    """
    #ok, user_or_msg = require_admin_identity()
    #if not ok:
    #    return jsonify({"error": user_or_msg}), 403

    prod = products.find_one({"sku": product_sku})
    if not prod:
        return jsonify({"error": "product not found"}), 404

    category = prod.get("category")
    sku_discount = product_discounts.find_one({"product_sku": product_sku, "active": True})
    cat_discount = product_discounts.find_one({"category": category, "active": True})

    sku_active = bool(sku_discount and is_discount_active(sku_discount))
    cat_active = bool(cat_discount and is_discount_active(cat_discount))

    return jsonify({
        "sku": product_sku,
        "category": category,
        "sku_has_active_discount": sku_active,
        "sku_discount": serialize_discount(sku_discount) if sku_discount else None,
        "category_has_active_discount": cat_active,
        "category_discount": serialize_discount(cat_discount) if cat_discount else None,
        "can_create_sku_discount": not sku_active,
        "can_create_category_discount": not cat_active
    }), 200
    
@product_discount_api.route("/preview", methods=["POST"])
def preview_discount():
    """
    Permite previsualizar un descuento sin guardarlo.
    Input:
    {
        "product_sku": "SKU123",
        "discount_type": "percentage" | "fixed",
        "value": <number>  # puede ser porcentaje o precio final
    }
    """
    data = request.get_json() or {}
    product_sku = data.get("product_sku")
    discount_type = data.get("discount_type")
    value = data.get("value")

    if not product_sku or not discount_type or value is None:
        return jsonify({"error": "product_sku, discount_type y value son requeridos"}), 400

    # validar producto existente
    prod = products.find_one({"sku": product_sku})
    if not prod:
        return jsonify({"error": "product not found"}), 404

    original_price = float(prod.get("price_sale", 0))

    # Validar tipo de descuento
    if discount_type not in ["percentage", "fixed"]:
        return jsonify({"error": "discount_type debe ser 'percentage' o 'fixed'"}), 400

    # Validar value
    try:
        val = float(value)
        if val <= 0:
            raise Exception()
    except:
        return jsonify({"error": "value debe ser un número positivo"}), 400

    # Crear un objeto ficticio de descuento para reusar compute_final_price
    fake_discount = {
        "discount_type": discount_type,
        "value": val,
        "active": True
    }

    final_price, savings_pct = compute_final_price(original_price, fake_discount)

    return jsonify({
        "original_price": original_price,
        "final_price": final_price,
        "savings_pct": savings_pct,
        "discount_type": discount_type,
        "value": val
    }), 200
    
@product_discount_api.route("/products", methods=["GET"])
def get_products_with_discounts():
    """
    Devuelve una lista de productos que tienen descuentos asociados
    (ya sea por SKU o por categoría).

    Resultado:
    [
        {
            "product": { ... info del producto ... },
            "discount": { ... descuento ... },
            "final_price": float,
            "savings_pct": float,
            "discount_origin": "sku" | "category"
        }
    ]
    """

    # 1. Obtener todos los descuentos (SKU o categoría)
    discounts = list(product_discounts.find({
        "active": True
    }))

    if not discounts:
        return jsonify([]), 200

    results = []

    # 2. Crear un mapa por categoría
    category_discounts = {}
    sku_discounts = {}

    for d in discounts:
        if d.get("product_sku"):
            sku_discounts[d["product_sku"]] = d
        elif d.get("category"):
            category_discounts[d["category"]] = d

    # 3. Buscar productos afectados por estos descuentos
    #    Si hay descuento por categoría, listar TODOS los productos de esa categoría.
    #    Si hay descuento por SKU, tomar solo ese producto.

    # A) Productos con descuento por SKU
    for sku, discount in sku_discounts.items():
        prod = products.find_one({"sku": sku})
        if not prod:
            continue

        # Validar vigencia por fecha
        if not is_discount_active(discount):
            continue

        original_price = float(prod.get("price_sale", 0))
        final_price, savings_pct = compute_final_price(original_price, discount)

        results.append({
            "product": {
                "sku": prod.get("sku"),
                "name": prod.get("name"),
                "category": prod.get("category"),
                "price_sale": original_price,
                "image": prod.get("image"),
                "status": prod.get("status"),
            },
            "discount": serialize_discount(discount),
            "discount_origin": "sku",
            "final_price": final_price,
            "savings_pct": savings_pct,
        })

    # B) Productos con descuento por categoría
    for category, discount in category_discounts.items():

        if not is_discount_active(discount):
            continue

        prods = list(products.find({"category": category}))

        for prod in prods:
            # Omitir si ya tiene descuento por SKU (prioridad)
            if prod.get("sku") in sku_discounts:
                continue

            original_price = float(prod.get("price_sale", 0))
            final_price, savings_pct = compute_final_price(original_price, discount)

            results.append({
                "product": {
                    "sku": prod.get("sku"),
                    "name": prod.get("name"),
                    "category": prod.get("category"),
                    "price_sale": original_price,
                    "image": prod.get("image"),
                    "status": prod.get("status"),
                },
                "discount": serialize_discount(discount),
                "discount_origin": "category",
                "final_price": final_price,
                "savings_pct": savings_pct,
            })

    return jsonify(results), 200

