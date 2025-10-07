import json
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
discounts_collection = db['discounts']  

class Discount:
    def __init__(self, 
                 id=None,
                 discount_code=None,
                 description=None,
                 discount_type=None,
                 value=None,
                 active=True,
                 start_date=None,
                 end_date=None,
                 customer_email=None
                 ):
        self.id = id
        self.discount_code = discount_code
        self.description = description
        self.discount_type = discount_type  # e.g., 'percentage' or 'fixed'
        self.value = value
        self.active = active
        self.start_date = start_date
        self.end_date = end_date
        self.customer_email = customer_email

    def save(self):
        discount_data = {
            "discount_code": self.discount_code,
            "description": self.description,
            "discount_type": self.discount_type,
            "value": self.value,
            "active": self.active,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "customer_email": self.customer_email
        }
        result = discounts_collection.insert_one(discount_data)
        self.id = result.inserted_id
        return self.id
    
    def update(self):
        discounts_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": { 
                        "discount_code": self.discount_code,
                        "description": self.description,
                        "discount_type": self.discount_type,
                        "value": self.value,
                        "active": self.active,
                        "start_date": self.start_date,
                        "end_date": self.end_date,
                        "customer_email": self.customer_email
                    }
            }
        )

    def to_json(self):
        discount_data = {
            "id": str(self.id),
            "discount_code": self.discount_code,
            "description": self.description,
            "discount_type": self.discount_type,
            "value": self.value,
            "active": self.active,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "customer_email": self.customer_email
        }
        return json.dumps(discount_data)


    @staticmethod
    def objects():
        return discounts_collection.find()

    @staticmethod
    def object(id):
        discount_data = discounts_collection.find_one({'_id': ObjectId(id)}, {'_id': 0})
        if discount_data:
            return Discount(**discount_data)
        else:
            return None

    @staticmethod
    def find_by_discount_code(discount_code):
        return discounts_collection.find_one({"discount_code": discount_code})

    @staticmethod
    def find_active_discounts():
        return discounts_collection.find({"active": True})

    @staticmethod
    def find_by_customer_email(customer_email, discount_code):
        return Discount(**discounts_collection.find_one({"customer_email": customer_email, "discount_code": discount_code, "active" : True}, {'_id': 0}))