from datetime import datetime
from bson import ObjectId
from ..db import get_db

db = get_db()
product_discounts = db["product_discounts"]

class ProductDiscount:
    def __init__(self,
                 id=None,
                 product_sku=None,
                 category=None,          # NUEVO → soporta descuentos por categoría
                 discount_type=None,     # "percentage" o "fixed"
                 value=None,
                 active=True,
                 start_date=None,
                 end_date=None,
                 created_at=None,
                 updated_at=None):
        
        self.id = id
        self.product_sku = product_sku
        self.category = category
        self.discount_type = discount_type
        self.value = value
        self.active = active
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def save(self):
        data = {
            "product_sku": self.product_sku,
            "category": self.category,             # NUEVO
            "discount_type": self.discount_type,
            "value": self.value,
            "active": self.active,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        res = product_discounts.insert_one(data)
        self.id = res.inserted_id
        return self.id

    def update(self):
        self.updated_at = datetime.utcnow()

        update_data = {
            "product_sku": self.product_sku,
            "category": self.category,
            "discount_type": self.discount_type,
            "value": self.value,
            "active": self.active,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "updated_at": self.updated_at
        }

        product_discounts.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": update_data}
        )

    @staticmethod
    def get_by_product(product_sku):
        """Obtiene el descuento activo por SKU."""
        return product_discounts.find_one({
            "product_sku": product_sku,
            "active": True
        })

    @staticmethod
    def get_by_category(category):
        """Obtiene el descuento activo por categoría."""
        return product_discounts.find_one({
            "category": category,
            "active": True
        })
