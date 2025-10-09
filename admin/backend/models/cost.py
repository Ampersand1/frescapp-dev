from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

from ..db import get_db
db = get_db()
costs_collection = db['costs']

class Cost:
    def __init__(self, typeCost, detail, amount, typePeriod, period, id=None):
        self.id = id  # Aquí `id` es opcional
        self.typeCost = typeCost
        self.detail = detail
        self.amount = amount
        self.typePeriod = typePeriod
        self.period = period

    def save(self):
        cost_data = {
            "typeCost": self.typeCost,
            "detail": self.detail,
            "amount": self.amount,
            "typePeriod": self.typePeriod,
            "period": self.period
        }
        result = costs_collection.insert_one(cost_data)
        self.id = str(result.inserted_id)
        return self.id

    def update(self):
        costs_collection.update_one(
           {"_id": ObjectId(self.id)},
            {"$set": {
                "typeCost": self.typeCost,
                "detail": self.detail,
                "amount": self.amount,
                "typePeriod": self.typePeriod,
                "period": self.period
            }}
        )

    @staticmethod
    def objects():
        return costs_collection.find()

    @staticmethod
    def object(id):
        cost_data = costs_collection.find_one({'_id': ObjectId(id)})
        if cost_data:
            cost_data['id'] = str(cost_data['_id'])
            return cost_data
        return None

    
    def deleteCost(self):
        result = costs_collection.delete_one({"_id": ObjectId(self.id)})
        if result.deleted_count > 0:
            print("Cost deleted successfully.")
        else:
            print("Cost not found.")
    
    @staticmethod
    def total_by_date_type(fecha):
        try:
            # Buscar todos los documentos en costs_collection que coincidan con la fecha
            costs = costs_collection.find({'period': fecha})
            
            total = 0  # Inicializar el total en 0
            
            # Recorrer cada documento de costos
            for cost in costs:
                # Verificar si el campo typecost es igual a "aux_ops"
                if cost.get("typecost") == "perssonel":
                    # Sumar el campo amount al total
                    total += cost.get("amount", 0)
            
            return total
        except Exception as e:
            print(f"Error al calcular el total para la fecha {fecha}: {e}")
            return 0
