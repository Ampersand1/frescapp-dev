from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from dateutil import parser as date_parser
from ..db import get_db
from flask_jwt_extended import jwt_required, get_jwt_identity
import math

db = get_db()
product_discounts = db["product_discounts"]
products_coll = db["products"]

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
    # Accept ISO strings, datetimes, or timestamp numbers
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, datetime):
        return value
    try:
        return date_parser.isoparse(value)
    except Exception:
        # fallback try common formats
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except Exception:
            return None


def is_discount_active(d):
    """Comprueba active flag y rango de fechas si aplica."""
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
    Si discount tiene 'discount_type' == 'fixed' y 'value' -> final = value
    Si 'percentage' -> final = product_price * (1 - value/100)
    Si mixed -> if fixed present prefer fixed, else percentage
    """
    if discount is None:
        return product_price, 0.0

    d_type = discount.get("discount_type")
    val = discount.get("value")
    if d_type == "fixed":
        try:
            final = float(val)
            savings_pct = (1 - (final / float(product_price))) * 100 if product_price and product_price > 0 else 0
            return round(final, 2), round(savings_pct, 2)
        except Exception:
            return product_price, 0.0
    elif d_type == "percentage":
        try:
            pct = float(val)
            pct = max(0.0, min(pct, 100.0))
            final = float(product_price) * (1 - (pct / 100.0))
            return round(final, 2), round(pct, 2)
        except Exception:
            return product_price, 0.0
    else:
        # fallback (if structure different)
        try:
            pct = float(val)
            final = float(product_price) * (1 - (pct / 100.0))
            return round(final, 2), round(pct, 2)
        except Exception:
            return product_price, 0.0


def require_admin_identity():
    """
    Extrae identidad del JWT y valida rol admin.
    Devuelve (True, user) o (False, msg)
    """
    try:
        user = get_jwt_identity() or {}
    except Exception:
        return False, "Invalid token or identity"
    # Ajusta según cómo guardes rol en tu JWT (role / is_admin)
    if isinstance(user, dict):
        if user.get("role") == "admin" or user.get("is_admin") == True:
            return True, user
    # si token existe pero no rol admin, denegar
    return False, "Unauthorized: admin role required"


# ---------------------------
# Routes
# ---------------------------

@product_discount_api.route("/create", methods=["POST"])
@jwt_required()
def create_product_discount():
    ok, user_or_msg = require_admin_identity()
    if not ok:
        return jsonify({"error": user_or_msg}), 403

    data = request.get_json() or {}
    product_sku = data.get("product_sku")
    discount_type = data.get("discount_type")  # 'percentage' or 'fixed'
    value = data.get("value")
    active = data.get("active", True)
    start_date = parse_optional_date(data.get("start_date"))
    end_date = parse_optional_date(data.get("end_date"))
    discount_category = data.get("category")

    # Validaciones 
    if not product_sku and not discount_category:
        return jsonify({"error": "Debe especificar product_sku o category"}), 400

    if product_sku and discount_category:
        return jsonify({"error": "No puede enviar product_sku y category al mismo tiempo"}), 400

    # 2. Validar discount_type
    if discount_type not in ["percentage", "fixed"]:
        return jsonify({"error": "discount_type debe ser 'percentage' o 'fixed'"}), 400

    # 3. Validar value numérico y positivo
    try:
        value = float(value)
        if value <= 0:
            raise Exception()
    except:
        return jsonify({"error": "value debe ser un número positivo"}), 400

    # 4. Validar SKU existente
    if product_sku:
        prod = products_coll.find_one({"sku": product_sku})
        if not prod:
            return jsonify({"error": "El SKU no existe en productos"}), 404

    # 5. Validar categoría existente
    if discount_category:
        exists = products_coll.find_one({"category": discount_category})
        if not exists:
            return jsonify({"error": "La categoría no existe en productos"}), 404

    # 6. Validar fechas
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")

    start_date = None
    end_date = None

    try:
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str)
        if start_date and end_date and start_date > end_date:
            return jsonify({"error": "start_date no puede ser mayor que end_date"}), 400
    except:
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400


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

    # Retornar el descuento y el precio final calculado para facilitar pruebas
    product_price = prod.get("price_sale", prod.get("price_sale") or 0)
    final_price, savings_pct = compute_final_price(product_price, doc)

    return jsonify({
        "message": "Discount created",
        "discount": serialize_discount(doc),
        "product": {
            "sku": product_sku,
            "original_price": product_price,
            "final_price": final_price,
            "savings_pct": savings_pct
        }
    }), 201


@product_discount_api.route("/<string:product_sku>", methods=["GET"])
def get_discount_by_sku(product_sku):
    prod = products_coll.find_one({"sku": product_sku})
    if not prod:
        return jsonify({"error": "product not found"}), 404

    category = prod.get("category")
    original_price = float(prod.get("price_sale", 0))

    # 1. Buscar descuento directo por producto
    discount = product_discounts.find_one({
        "product_sku": product_sku,
        "active": True
    })

    # 2. Si no hay, buscar descuento por categoría
    if not (discount and is_discount_active(discount)):
        discount = product_discounts.find_one({
            "category": category,
            "active": True
        })

    if discount and is_discount_active(discount):
        final_price, savings_pct = compute_final_price(original_price, discount)
        return jsonify({
            "discount": serialize_discount(discount),
            "product": {
                "sku": product_sku,
                "category": category,
                "original_price": original_price,
                "final_price": final_price,
                "savings_pct": savings_pct
            }
        }), 200

    return jsonify({
        "message": "No active discount",
        "product": {
            "sku": product_sku,
            "category": category,
            "original_price": original_price,
            "final_price": original_price,
            "savings_pct": 0.0
        }
    }), 200


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

    prod = products_coll.find_one({"sku": product_sku, "status": {"$in": ["active", None]}})
    if not prod:
        return jsonify({"error": "product not found"}), 404

    # buscar descuento activo
    discount = product_discounts.find_one({
        "product_sku": product_sku,
        "active": True
    })

    original_price = float(prod.get("price_sale", 0))
    if discount and is_discount_active(discount):
        final_price, savings_pct = compute_final_price(original_price, discount)
        return jsonify({
            "sku": product_sku,
            "original_price": original_price,
            "final_price": final_price,
            "savings_pct": savings_pct,
            "discount": serialize_discount(discount)
        }), 200

    return jsonify({
        "sku": product_sku,
        "original_price": original_price,
        "final_price": original_price,
        "savings_pct": 0.0,
        "discount": None
    }), 200


@product_discount_api.route("/<string:discount_id>", methods=["PUT"])
@jwt_required()
def update_product_discount(discount_id):
    ok, user_or_msg = require_admin_identity()
    if not ok:
        return jsonify({"error": user_or_msg}), 403

    discount = product_discounts.find_one({"_id": ObjectId(discount_id)})
    if not discount:
        return jsonify({"error": "discount not found"}), 404

    data = request.get_json() or {}
    update = {}

    if "discount_type" in data:
        if data["discount_type"] not in ("percentage", "fixed"):
            return jsonify({"error": "invalid discount_type"}), 400
        update["discount_type"] = data["discount_type"]

    if "value" in data:
        try:
            val = float(data["value"])
            if update.get("discount_type", discount.get("discount_type")) == "percentage" and (val < 0 or val > 100):
                return jsonify({"error": "percentage must be between 0 and 100"}), 400
            update["value"] = val
        except Exception:
            return jsonify({"error": "value must be numeric"}), 400

    if "active" in data:
        update["active"] = bool(data["active"])

    if "start_date" in data:
        parsed = parse_optional_date(data.get("start_date"))
        if not parsed:
            return jsonify({"error": "invalid start_date"}), 400
        update["start_date"] = parsed

    if "end_date" in data:
        parsed = parse_optional_date(data.get("end_date"))
        if not parsed:
            return jsonify({"error": "invalid end_date"}), 400
        update["end_date"] = parsed

    if "start_date" in update and "end_date" in update and update["start_date"] and update["end_date"] and update["start_date"] > update["end_date"]:
        return jsonify({"error": "start_date must be before end_date"}), 400

    update["updated_at"] = datetime.utcnow()
    product_discounts.update_one({"_id": ObjectId(discount_id)}, {"$set": update})

    updated = product_discounts.find_one({"_id": ObjectId(discount_id)})
    return jsonify({"message": "discount updated", "discount": serialize_discount(updated)}), 200


@product_discount_api.route("/<string:discount_id>", methods=["DELETE"])
@jwt_required()
def delete_product_discount(discount_id):
    ok, user_or_msg = require_admin_identity()
    if not ok:
        return jsonify({"error": user_or_msg}), 403

    discount = product_discounts.find_one({"_id": ObjectId(discount_id)})
    if not discount:
        return jsonify({"error": "discount not found"}), 404

    product_discounts.update_one({"_id": ObjectId(discount_id)}, {"$set": {"active": False, "updated_at": datetime.utcnow()}})
    return jsonify({"message": "discount disabled"}), 200


@product_discount_api.route("/all", methods=["GET"])
@jwt_required()
def get_all_discounts():
    ok, user_or_msg = require_admin_identity()
    if not ok:
        return jsonify({"error": user_or_msg}), 403

    docs = list(product_discounts.find().sort([("created_at", -1)]))
    serialized = [serialize_discount(d) for d in docs]
    return jsonify(serialized), 200

@product_discount_api.route("/category/<string:category>", methods=["GET"])
def get_discount_by_category(category):
    discount = product_discounts.find_one({
        "category": category,
        "active": True
    })

    if discount and is_discount_active(discount):
        return jsonify(serialize_discount(discount)), 200

    return jsonify({"message": "No active discount for this category"}), 200

