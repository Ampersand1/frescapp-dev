import json
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
orders_collection = db['orders']  

class Order:
    def __init__(self, 
                 id=None,
                 order_number=None,
                 customer_email=None, 
                 customer_phone=None,
                 customer_documentNumber=None,
                 customer_documentType=None,
                 customer_name=None,
                 delivery_date=None, 
                 status=None, 
                 created_at=None, 
                 updated_at=None, 
                 products=None,
                 total=None,
                 deliverySlot=None,
                 paymentMethod=None,
                 deliveryAddress=None,
                 deliveryAddressDetails=None,
                 discount=0,
                 deliveryCost=None,
                 alegra_id=None,
                 open_hour=None,
                 payment_date=None,
                 driver_name=None,
                 seller_name=None,
                 source=None,
                 totalPayment=None
                 ,status_payment='Pendiente de pago'):
        self.id = id
        self.order_number = order_number
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.customer_documentNumber = customer_documentNumber
        self.customer_documentType = customer_documentType
        self.customer_name = customer_name
        self.delivery_date = delivery_date
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.products = products if products is not None else []
        self.total = total
        self.deliverySlot = deliverySlot
        self.paymentMethod = paymentMethod
        self.deliveryAddress = deliveryAddress
        self.deliveryAddressDetails = deliveryAddressDetails
        self.discount = discount  # Default value is 0
        self.deliveryCost = deliveryCost if deliveryCost is not None else 0
        self.alegra_id = alegra_id if alegra_id is not None else "000"
        self.open_hour = open_hour if open_hour is not None else ""
        self.payment_date = payment_date if payment_date is not None else delivery_date
        self.driver_name = driver_name if driver_name is not None else ''
        self.seller_name = seller_name if seller_name is not None else ''
        self.source = source if source is not None else 'app'
        self.totalPayment = totalPayment if totalPayment is not None else 0
        self.status_payment = status_payment if status_payment is not None else 'Pendiente de pago'

    def save(self):
        order_data = {
            "order_number" : self.order_number,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "customer_documentNumber": self.customer_documentNumber,
            "customer_documentType": self.customer_documentType,
            "customer_name": self.customer_name,
            "delivery_date": self.delivery_date,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at" : self.updated_at,
            "products" : self.products,
            "total" : self.total,
            "deliverySlot" : self.deliverySlot,
            "paymentMethod" : self.paymentMethod,
            "deliveryAddress" : self.deliveryAddress,
            "deliveryAddressDetails" : self.deliveryAddressDetails,
            "discount" : self.discount,
            "deliveryCost" : self.deliveryCost,
            "alegra_id" :self.alegra_id,
            "open_hour" :self.open_hour or '',
            "payment_date" : self.payment_date or self.delivery_date,
            "driver_name" : self.driver_name or '',
            "seller_name" : self.seller_name or '',
            "source" : self.source or 'app',
            "totalPayment" : self.totalPayment or 0,
            "status_payment" : self.status_payment or 'Pendiente de pago'
        }
        result = orders_collection.insert_one(order_data)
        return result.inserted_id
    
    def updated(self):
        new_total = sum(
            p.get('price_sale', 0) * p.get('quantity', 1)
            for p in self.products
        )
        orders_collection.update_one(
            {"_id": ObjectId(self.id)},  # Usamos el ObjectId correctamente
            {"$set": { 
                "order_number" :self.order_number,
                "customer_email": self.customer_email,
                "customer_phone": self.customer_phone,
                "customer_documentNumber": self.customer_documentNumber,
                "customer_documentType": self.customer_documentType,
                "customer_name": self.customer_name,
                "delivery_date": self.delivery_date,
                "status": self.status,
                "created_at": self.created_at,
                "updated_at" : self.updated_at,
                "products" : self.products,
                "total" : new_total,
                "deliverySlot" : self.deliverySlot,
                "paymentMethod" : self.paymentMethod,
                "deliveryAddress" : self.deliveryAddress,
                "deliveryAddressDetails" : self.deliveryAddressDetails,
                "discount" : self.discount,
                "alegra_id" :self.alegra_id,
                "open_hour" :self.open_hour or '',
                "payment_date" : self.payment_date or self.delivery_date,
                "driver_name" : self.driver_name or '',
                "seller_name" : self.seller_name or '',
                "source" : self.source or 'app',
                "totalPayment" : self.totalPayment or 0,
                "status_payment" : self.status_payment or 'Pendiente de pago'
                }
            }
        )
    def to_json(self):

        order_data = {
            "order_number": self.order_number,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "customer_documentNumber": self.customer_documentNumber,
            "customer_documentType": self.customer_documentType,
            "customer_name": self.customer_name,
            "delivery_date": self.delivery_date,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "products": self.products,
            "total": self.total,
            "deliverySlot": self.deliverySlot,
            "paymentMethod": self.paymentMethod,
            "deliveryAddress": self.deliveryAddress,
            "deliveryAddressDetails": self.deliveryAddressDetails,
            "discount": self.discount,
            "deliveryCost": self.deliveryCost,
            "alegra_id" : self.alegra_id,
            "open_hour" : self.open_hour,
            "payment_date" : self.payment_date,
            "driver_name" : self.driver_name,
            "seller_name" : self.seller_name,
            "source" : self.source,
            "totalPayment" : self.totalPayment
        }
        return json.dumps(order_data)
    def delete_order(self):
        if not self.id:
            raise ValueError("Order ID is required for deletion.")

        # Verifica si el id es una cadena o un ObjectId
        if isinstance(self.id, str):
            self.id = ObjectId(self.id)

        if not isinstance(self.id, ObjectId):
            raise ValueError(f"Invalid ID type: {type(self.id)}")

        result = orders_collection.delete_one({"_id": self.id})

    @staticmethod
    def objects():
        return orders_collection.find()
    @staticmethod
    def objects_date(stratDate, endDate):
        return orders_collection.find({"delivery_date": {"$gte": stratDate, "$lte": endDate}})
    @staticmethod
    def object(id):
        if isinstance(id, str):
            id = ObjectId(id)

        order_data = orders_collection.find_one({'_id': id})
        if order_data:
            order_data['id'] = str(order_data.pop('_id'))
            return Order(**order_data)
        else:
            return None

    @staticmethod
    def find_by_order_number(order_number):
        order_data = orders_collection.find_one({"order_number": order_number})
        if order_data:
            order_data['id'] = ObjectId(order_data.pop('_id'))
            return Order(**order_data)
        else:
            return None

    @staticmethod
    def find_by_customer(customer_email):
        return orders_collection.find({"customer_email": customer_email})
    @staticmethod
    def find_by_status(status):
        return orders_collection.find({"status": status})
    @staticmethod
    def find_by_status_payment(status):
        return orders_collection.find({"status_payment": status})
    @staticmethod
    def find_by_date(startDate, endDate):        
        return orders_collection.find({
            "delivery_date": {
                "$gte": startDate,  # Mayor o igual que startDate
                "$lte": endDate     # Menor o igual que endDate
            }
        })
