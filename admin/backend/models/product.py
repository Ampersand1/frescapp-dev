from bson import ObjectId
from datetime import datetime
from ..db import get_db

db = get_db()
products_collection = db["products"]


class Product:

    def __init__(
        self,
        id=None,
        sku=None,
        name=None,
        description="",
        category="General",
        root=None,
        child=None,
        unit="Unidad",

        price_sale=0.0,
        price_purchase=0.0,

        # Deprecated: ya no se usa, pero se mantiene por compatibilidad
        discount=0.0,

        margen=0.0,
        iva=0.0,
        iva_value=0.0,

        proveedor=None,
        step_unit=1,

        # Visible para cliente
        is_visible=True,

        # Campos adicionales del sistema
        tipo_pricing=None,
        rate_root=None,
        factor_volumen=None,
        sipsa_id=None,
        last_price_purchase=None,

        status="active",
        created_at=None,
        updated_at=None,
    ):
        self.id = str(id) if id else None

        self.sku = sku
        self.name = name
        self.description = description

        self.category = category
        self.root = root
        self.child = child
        self.unit = unit

        self.price_sale = float(price_sale)
        self.price_purchase = float(price_purchase)
        self.discount = float(discount)  # No se usa para cálculos nuevos

        self.margen = float(margen)
        self.iva = float(iva)
        self.iva_value = float(iva_value)

        self.proveedor = proveedor
        self.step_unit = float(step_unit)

        self.is_visible = bool(is_visible)

        self.tipo_pricing = tipo_pricing
        self.rate_root = rate_root
        self.factor_volumen = factor_volumen
        self.sipsa_id = sipsa_id
        self.last_price_purchase = last_price_purchase

        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()


    def to_dict(self):
        return {
            "sku": self.sku,
            "name": self.name,
            "description": self.description,

            "category": self.category,
            "root": self.root,
            "child": self.child,
            "unit": self.unit,

            "price_sale": self.price_sale,
            "price_purchase": self.price_purchase,

            "discount": self.discount,  # deprecated

            "margen": self.margen,
            "iva": self.iva,
            "iva_value": self.iva_value,

            "proveedor": self.proveedor,
            "step_unit": self.step_unit,

            "is_visible": self.is_visible,

            "tipo_pricing": self.tipo_pricing,
            "rate_root": self.rate_root,
            "factor_volumen": self.factor_volumen,
            "sipsa_id": self.sipsa_id,
            "last_price_purchase": self.last_price_purchase,

            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


    def save(self):
        data = self.to_dict()
        result = products_collection.insert_one(data)
        self.id = str(result.inserted_id)
        return self.id


    def update(self):
        if not self.id:
            raise ValueError("Producto sin ID no se puede actualizar")

        self.updated_at = datetime.utcnow()

        products_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": self.to_dict()}
        )


    def delete(self):
        if not self.id:
            return
        products_collection.delete_one({"_id": ObjectId(self.id)})


    @staticmethod
    def find_by_sku(sku):
        doc = products_collection.find_one({"sku": sku})
        if not doc:
            return None
        doc["id"] = str(doc["_id"])
        return doc

    @staticmethod
    def find_by_category(category):
        return list(products_collection.find({"category": category}))

    @staticmethod
    def get_all():
        items = list(products_collection.find())
        for i in items:
            i["id"] = str(i["_id"])
        return items
@staticmethod
def objects(status=None):
    if status:
        return products_collection.find({"status": status})
    return products_collection.find()
@staticmethod
def objects_customer(customer_email):
    customers_collection = db["customers"]

    if customer_email == "undefined":
        customer_product_skus = [
            'BOG-CAT003-00029','BOG-CAT001-00002','BOG-CAT001-00007','BOG-CAT001-00004',
            'BOG-CAT002-00001','BOG-CAT001-00005','BOG-CAT004-00001','BOG-CAT004-00003',
            'BOG-CAT001-00001','BOG-CAT001-00003','BOG-CAT001-00006','BOG-CAT001-00013',
            'BOG-CAT004-00011','BOG-CAT001-00017','BOG-CAT001-00008','BOG-CAT003-00005',
            'BOG-CAT002-00007','BOG-CAT004-00004','BOG-CAT003-00003','BOG-CAT001-00015',
            'BOG-CAT001-00020','BOG-CAT004-00024','BOG-CAT002-00008','BOG-CAT001-00042',
            'BOG-CAT002-00004','BOG-CAT001-00057','BOG-CAT001-00014','BOG-CAT002-00036',
            'BOG-CAT004-00006','BOG-CAT002-00002','BOG-CAT001-00009'
        ]
    else:
        customer = customers_collection.find_one({"email": customer_email})
        customer_product_skus = customer.get("list_products", []) if customer else []

    all_active_products = list(products_collection.find({"is_visible": True}))

    product_dict = {p["sku"]: p for p in all_active_products}

    ordered_products = []

    for sku in customer_product_skus:
        if sku in product_dict:
            ordered_products.append(product_dict.pop(sku))

    ordered_products.extend(list(product_dict.values()))

    return ordered_products
@classmethod
def find_for_customer(cls, email):
    db = get_db()
    customers = db["customers"]

    customer = customers.find_one({"email": email})
    if not customer or "match_catalogo" not in customer:
        return []

    skus = [
        item.get("sku")
        for item in customer["match_catalogo"]
        if item.get("sku")
    ]

    return list(db["products"].find({
        "sku": {"$in": skus},
        "status": "active"
    }))

