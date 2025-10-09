from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

from ..db import get_db
db = get_db()
customers_collection = db['customers']  

class Customer:
    def __init__(self, 
                 phone, 
                 name, 
                 document,
                 document_type,
                 address, 
                 restaurant_name,
                 email, 
                 status, 
                 created_at, 
                 updated_at, 
                 password,
                 category,
                 list_products,
                 role,
                 user,
                 open_hour=''):
        self.phone = phone
        self.name = name
        self.document = document
        self.document_type = document_type
        self.address = address
        self.restaurant_name = restaurant_name
        self.email = email
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.password = password
        self.category = category
        self.list_products = list_products,
        self.role = role
        self.user = user
        self.open_hour = open_hour
    def save(self):
        customer_data = {
            "phone": self.phone,
            "name": self.name,
            "document": self.document,
            "document_type": self.document_type,
            "address": self.address,
            "restaurant_name": self.restaurant_name,
            "email": self.email,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at" : self.updated_at,
            "password" : self.password,
            "category" : self.category,
            "list_products" : self.list_products,
            "role" : self.role,
            "user" : self.user
        }
        result = customers_collection.insert_one(customer_data)
        return result.inserted_id
    
    def updated(self):
        customers_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": { 
                        "phone": self.phone,
                        "name": self.name,
                        "document": self.document,
                        "document_type": self.document_type,
                        "address": self.address,
                        "restaurant_name" : self.restaurant_name,
                        "email": self.email,
                        "status": self.status,
                        "created_at": self.created_at,
                        "updated_at" : self.updated_at,
                        "password" : self.password,
                        "category" : self.category,
                        "list_products" : self.list_products,
                        "role" : self.role
                    }
            }
        )
    

    @staticmethod
    def objects():
        return customers_collection.find()
    @staticmethod
    def object(id):
        customer_data = customers_collection.find_one({'_id': ObjectId(id) }, {'_id': 0})
        if customer_data:
            return Customer(**customer_data)
        else:
            return None
    @staticmethod
    def find_by_email(email):
        return customers_collection.find_one({"email": email})