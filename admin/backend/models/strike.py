# Backend: app/models/strike_model.py

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# MongoDB connection
from ..db import get_db
db = get_db()
strikes_collection = db['strikes']

class Strike:
    def __init__(self, order_number, sku, strike_type, missing_quantity, detail, timestamp=None, id=None,name=None):
        self.id = id
        self.order_number = order_number       # order number
        self.sku = sku                         # item SKU (or None if whole-order strike)
        self.name = name                       # item name (or None if whole-order strike)
        self.strike_type = strike_type         # e.g. quality, partial_missing, etc.
        self.missing_quantity = missing_quantity  # quantity missing, if applicable
        self.detail = detail                   # description or reason
        self.timestamp = timestamp if timestamp is not None else datetime.utcnow()

    def save(self):
        data = {
            "order_number": self.order_number,
            "sku": self.sku,
            "name": self.name,  # Include name for item strike
            "strike_type": self.strike_type,
            "missing_quantity": self.missing_quantity,
            "detail": self.detail,
            "timestamp": self.timestamp
        }
        result = strikes_collection.insert_one(data)
        self.id = str(result.inserted_id)
        return self.id

    def update(self):
        if not self.id:
            raise ValueError("Must specify id to update a strike.")
        strikes_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "order_number": self.order_number,
                "sku": self.sku,
                "name": self.name,  # Update name for item strike
                "strike_type": self.strike_type,
                "missing_quantity": self.missing_quantity,
                "detail": self.detail,
                "timestamp": self.timestamp
            }}
        )

    def delete(self):
        if not self.id:
            raise ValueError("Must specify id to delete a strike.")
        strikes_collection.delete_one({"_id": ObjectId(self.id)})

    @staticmethod
    def all(limit=0):
        cursor = strikes_collection.find().sort("timestamp", -1)
        if limit:
            cursor = cursor.limit(limit)
        docs = []
        for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            docs.append(doc)
        return docs

    @staticmethod
    def get(id):
        doc = strikes_collection.find_one({"_id": ObjectId(id)})
        if doc:
            doc['id'] = str(doc.pop('_id'))
            return doc
        return None

    @staticmethod
    def find_by_order(order_number):
        cursor = strikes_collection.find({"order_number": order_number}).sort("timestamp", -1)
        docs = []
        for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            docs.append(doc)
        return docs