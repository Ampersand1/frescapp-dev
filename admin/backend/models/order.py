import json
from datetime import datetime
from bson import ObjectId

from ..db import get_db
db = get_db()
orders_collection = db["orders"]


class Order:
    def __init__(
        self,
        id=None,
        order_number=None,
        customer_email=None,
        customer_phone=None,
        customer_documentNumber=None,
        customer_documentType=None,
        customer_name=None,
        delivery_date=None,
        status="Creada",
        created_at=None,
        updated_at=None,
        products=None,
        total=0.0,
        deliverySlot="09:00-12:00",
        paymentMethod="Cash",
        deliveryAddress="",
        deliveryAddressDetails="",
        deliveryCost=0.0,
        discount=0.0,
        alegra_id="000",
        open_hour="",
        payment_date=None,
        driver_name="",
        seller_name="",
        source="Aplicación",
        totalPayment=0.0,
        status_payment="Pendiente",
    ):

        self.id = str(id) if id else None
        self.order_number = order_number

        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.customer_documentNumber = customer_documentNumber
        self.customer_documentType = customer_documentType
        self.customer_name = customer_name

        self.delivery_date = delivery_date
        self.status = status

        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

        self.products = self._normalize_products(products or [])
        self.total = float(total)

        self.deliverySlot = deliverySlot
        self.paymentMethod = paymentMethod
        self.deliveryAddress = deliveryAddress
        self.deliveryAddressDetails = deliveryAddressDetails

        self.deliveryCost = float(deliveryCost)
        self.discount = float(discount)
        self.alegra_id = alegra_id

        self.open_hour = open_hour
        self.payment_date = payment_date or delivery_date

        self.driver_name = driver_name
        self.seller_name = seller_name
        self.source = source

        self.totalPayment = float(totalPayment)
        self.status_payment = status_payment

    # ----------------------------------------------------
    # Normalización de productos
    # ----------------------------------------------------
    def _normalize_products(self, products):
        normalized = []
        for p in products:
            normalized.append({
                "sku": p.get("sku"),
                "name": p.get("name"),
                "quantity": float(p.get("quantity", 0)),
                "price_sale": float(p.get("price_sale", 0)),
                "unit": p.get("unit", "")
            })
        return normalized

    # ----------------------------------------------------
    # Guardar
    # ----------------------------------------------------
    def save(self):
        data = self._to_mongo_dict()
        result = orders_collection.insert_one(data)
        self.id = str(result.inserted_id)
        return self.id

    # ----------------------------------------------------
    # Actualizar
    # ----------------------------------------------------
    def updated(self):
        if not self.id:
            raise ValueError("No se puede actualizar una orden sin ID")

        self.updated_at = datetime.now().isoformat()

        update_data = self._to_mongo_dict()

        orders_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": update_data}
        )

    # ----------------------------------------------------
    # Eliminar
    # ----------------------------------------------------
    def delete_order(self):
        if not self.id:
            return
        orders_collection.delete_one({"_id": ObjectId(self.id)})

    # ----------------------------------------------------
    # Convertir a dict para Mongo
    # ----------------------------------------------------
    def _to_mongo_dict(self):
        return {
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
            "deliveryCost": self.deliveryCost,
            "discount": self.discount,
            "alegra_id": self.alegra_id,
            "open_hour": self.open_hour,
            "payment_date": self.payment_date,
            "driver_name": self.driver_name,
            "seller_name": self.seller_name,
            "source": self.source,
            "totalPayment": self.totalPayment,
            "status_payment": self.status_payment,
        }

    # ----------------------------------------------------
    # Para enviar a frontend
    # ----------------------------------------------------
    def to_json(self):
        data = self._to_mongo_dict()
        data["id"] = self.id
        return json.dumps(data)

    # ----------------------------------------------------
    # BUSQUEDAS
    # ----------------------------------------------------
    @staticmethod
    def objects():
        return orders_collection.find()

    @staticmethod
    def object(id):
        doc = orders_collection.find_one({"_id": ObjectId(id)})
        if not doc:
            return None

        # Normalizar llaves antiguas
        doc = Order._normalize_old_keys(doc)

        return Order(id=str(doc["_id"]), **doc)

    @staticmethod
    def find_by_order_number(order_number):
        doc = orders_collection.find_one({"order_number": order_number})
        if not doc:
            return None

        doc = Order._normalize_old_keys(doc)
        return Order(id=str(doc["_id"]), **doc)

    @staticmethod
    def find_by_customer(email):
        return orders_collection.find({"customer_email": email})

    @staticmethod
    def find_by_date(start, end):
        return orders_collection.find({
            "delivery_date": {"$gte": start, "$lte": end}
        })

    @staticmethod
    def find_by_status_payment(status):
        return orders_collection.find({"status_payment": status})

    # ----------------------------------------------------
    # Normalizar campos antiguos → nuevos
    # ----------------------------------------------------
    @staticmethod
    def _normalize_old_keys(doc):
        if "customerName" in doc:
            doc["customer_name"] = doc.pop("customerName")
        if "customerEmail" in doc:
            doc["customer_email"] = doc.pop("customerEmail")
        if "deliveryDate" in doc:
            doc["delivery_date"] = doc.pop("deliveryDate")
        if "orderNumber" in doc:
            doc["order_number"] = doc.pop("orderNumber")

        return doc
