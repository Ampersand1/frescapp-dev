from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import json

from ..db import get_db
db = get_db()
purchase_collection = db['purchases']  
class Purchase:
    def __init__(self, 
                 date=None, 
                 purchase_number=None, 
                 status=None,
                 products = None,
                 comments =None,
                efectivoEntreado=0,
                 _id=None):
        self.date = date
        self.purchase_number = purchase_number
        self.status = status
        self.products = products if products is not None else [] 
        self.comments = comments if comments is not None else ""
        self.efectivoEntreado = efectivoEntreado
        self.id = _id
    @staticmethod
    def total_by_date(fecha):
        try:
            purchase = purchase_collection.find_one({"date": fecha})
            
            if not purchase:
                return 0  # Si no hay inventario para esa fecha, retornar 0
            
            products = purchase.get("products", [])
        
            total = sum((product.get("final_price_purchase") or 0) * (product.get("total_quantity") or 0) for product in products)
            
            return total
        except Exception as e:
            print(f"Error al calcular el total para la fecha {fecha}: {e}")
            return 0
    @staticmethod
    def get_by_date(fecha):
        purchase = purchase_collection.find_one({"date": fecha})
        if purchase:
            return Purchase(
                date=purchase.get("date"),
                purchase_number=purchase.get("purchase_number"),
                efectivoEntreado=purchase.get("efectivoEntreado", 0),
                status=purchase.get("status"),
                products=purchase.get("products"),
                comments = purchase.get("comments"),
                _id=str(purchase["_id"])
            )
        return None
    @staticmethod
    def get_by_number(purchase_number):
        purchase = purchase_collection.find_one({"purchase_number": purchase_number})
        if purchase:
            return Purchase(
                date=purchase.get("date"),
                purchase_number=purchase.get("purchase_number"),
                status=purchase.get("status"),
                products=purchase.get("products"),
                comments = purchase.get("comments"),
                _id=str(purchase["_id"])
            )
        return None
    def delete(self):
        result = purchase_collection.delete_one({"_id": ObjectId(self.id)})
        return result.deleted_count > 0
    def to_dict(self):
        """Devuelve un dict listo para serializar."""
        return {
            "id": str(self.id),
            "date": self.date.isoformat() if isinstance(self.date, datetime) else self.date,
            "purchase_number": self.purchase_number,
            "status": self.status,
            "products": self.products,
            "comments": self.comments
        }

    def to_json(self):
        """Devuelve un string JSON (sin pérdidas de caracteres unicode)."""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            default=str  # para cualquier otro tipo no serializable
        )