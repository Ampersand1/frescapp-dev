from datetime import datetime
from bson import ObjectId
from ..db import get_db

db = get_db()
product_discounts = db["product_discounts"]

class ProductDiscount:
    def __init__(self,
                 id=None,
                 product_sku=None,
                 discount_type=None,   # "percentage" o "fixed"
                 value=None,
                 active=True,
                 start_date=None,
                 end_date=None):
        self.id = id
        self.product_sku = product_sku
        self.discount_type = discount_type
        self.value = value
        self.active = active
        self.start_date = start_date
        self.end_date = end_date

    def save(self):
        data = {
            "product_sku": self.product_sku,
            "discount_type": self.discount_type,
            "value": self.value,
            "active": self.active,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "created_at": datetime.utcnow()
        }
        res = product_discounts.insert_one(data)
        self.id = res.inserted_id
        return self.id

    def update(self):
        product_discounts.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "product_sku": self.product_sku,
                "discount_type": self.discount_type,
                "value": self.value,
                "active": self.active,
                "start_date": self.start_date,
                "end_date": self.end_date
            }}
        )

    @staticmethod
    def get_by_product(product_sku):
        return product_discounts.find_one({
            "product_sku": product_sku,
            "active": True
        })
