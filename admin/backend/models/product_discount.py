# models/product_discount.py
from datetime import datetime
from bson import ObjectId
from ..db import get_db

db = get_db()
product_discounts = db["product_discounts"]
products = db["products"]  # si lo necesitas en métodos futuros


class ProductDiscount:
    """
    Modelo minimal y centralizado para descuentos.
    - Provee compatibilidad con llamadas antiguas (objects_active)
    - Provee funciones útiles: apply_discount_to_price, compute_percentage, get_best_discount, is_active, serialize
    """

    @staticmethod
    def serialize(doc):
        if not doc:
            return None
        return {
            "id": str(doc.get("_id")),
            "product_sku": doc.get("product_sku"),
            "category": doc.get("category"),
            "discount_type": doc.get("discount_type"),
            "value": float(doc.get("value", 0)),
            "active": bool(doc.get("active", True)),
            "start_date": doc.get("start_date"),
            "end_date": doc.get("end_date"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

    @staticmethod
    def is_active(doc):
        """Comprueba flag active y rango de fechas."""
        if not doc or not doc.get("active", True):
            return False

        now = datetime.utcnow()
        start = doc.get("start_date")
        end = doc.get("end_date")

        # Si vienen como strings/other, intentar parsear sería otra mejora.
        if start and not isinstance(start, datetime):
            try:
                # mongo suele guardar datetimes, pero por si acaso:
                start = datetime.fromisoformat(start)
            except Exception:
                start = None
        if end and not isinstance(end, datetime):
            try:
                end = datetime.fromisoformat(end)
            except Exception:
                end = None

        if start and now < start:
            return False
        if end and now > end:
            return False
        return True

    # ----------------------------
    # Compatibilidad: objeto listado
    # ----------------------------
    @staticmethod
    def objects_active():
        """
        Devuelve lista de documentos de descuentos activos (sin serializar).
        Mantiene compatibilidad con implementaciones anteriores.
        """
        docs = list(product_discounts.find({"active": True}))
        # Opcional: filtrar por fecha con is_active
        filtered = [d for d in docs if ProductDiscount.is_active(d)]
        return filtered

    # ----------------------------
    # Obtener "mejor" descuento (SKU > category)
    # ----------------------------
    @staticmethod
    def get_best_discount(sku, category=None):
        if not sku and not category:
            return None

        # Prioridad SKU
        if sku:
            d = product_discounts.find_one({"product_sku": sku, "active": True})
            if d and ProductDiscount.is_active(d):
                return d

        # Fallback categoría
        if category:
            d = product_discounts.find_one({"category": category, "active": True})
            if d and ProductDiscount.is_active(d):
                return d

        return None

    # ----------------------------
    # Aplicar descuento a un precio (devuelve precio final)
    # - fixed: value = precio final
    # - percentage: value = porcentaje (0-100)
    # ----------------------------
    @staticmethod
    def apply_discount_to_price(original_price, discount_type, value):
        try:
            original_price = float(original_price or 0.0)
            value = float(value or 0.0)
        except Exception:
            return float(original_price)

        if value <= 0:
            return float(round(original_price, 2))

        if discount_type == "fixed":
            # value es precio final. Nunca mayor que el precio original.
            final = max(0.0, min(value, original_price))
            return round(final, 2)

        # percentage (o fallback)
        pct = max(0.0, min(value, 100.0))
        final = original_price * (1 - pct / 100.0)
        return round(final, 2)

    # ----------------------------
    # Calcular porcentaje de ahorro (0..100)
    # ----------------------------
    @staticmethod
    def compute_percentage(original_price, final_price):
        try:
            original = float(original_price or 0.0)
            final = float(final_price or 0.0)
            if original <= 0:
                return 0.0
            pct = (1 - final / original) * 100
            return round(max(0.0, min(pct, 100.0)), 2)
        except Exception:
            return 0.0
