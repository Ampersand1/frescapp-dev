from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
routes_collection = db['routes']

class Route:
    def __init__(self, route_number, close_date,  stops=None, cost=0, id=None,status="Programada"):
        self.id = id  # Aquí `id` es opcional
        self.route_number = route_number
        self.close_date = close_date
        self.stops = stops if stops is not None else []
        self.cost = cost
        self.status = status

    def save(self):
        route_data = {
            "route_number": self.route_number,
            "close_date": self.close_date,
            "stops": self.stops,
            "cost": self.cost,
            "status": self.status if hasattr(self, 'status') else "Programada"  
        }
        result = routes_collection.insert_one(route_data)
        self.id = str(result.inserted_id)
        return self.id

    def update(self):
        routes_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "route_number": self.route_number,
                "close_date": self.close_date,
                "stops": self.stops,
                "cost": self.cost,
                "status": self.status if hasattr(self, 'status') else "Programada"
            }}
        )
    def close_route(self):
        routes_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "route_number": self.route_number,
                "close_date": self.close_date,
                "stops": self.stops,
                "cost": self.cost,
                "status": "Cerrada"
            }}
        )
    @staticmethod
    def objects():
        return routes_collection.find().sort("close_date", -1).limit(50)

    @staticmethod
    def object(id):
        route_data = routes_collection.find_one({'_id': ObjectId(id)})
        if route_data:
            route_data['id'] = str(route_data['_id'])
            return route_data
        return None

    @staticmethod
    def find_by_route_number(route_number):
        route = routes_collection.find_one({"route_number": int(route_number)})
        if route:
            route['id'] = str(route['_id'])
        return route
    @staticmethod
    def find_by_date(date):
        route = routes_collection.find_one({"close_date": date})
        if route:
            route['id'] = str(route['_id'])
            return Route(
                route_number = route.get("route_number"),
                close_date   = route.get("close_date"),
                stops        = route.get("stops", []),
                cost         = route.get("cost", 0),
                id           = str(route.get("_id")),
                status       = route.get("status", "Programada")
        )
        else:
            return None
    
    def delete_route(self):
        routes_collection.delete_one({"_id": ObjectId(self.id)})

    def to_dict(self):
        """Devuelve un dict listo para serializar a JSON."""
        return {
            "id": str(self.id),
            "route_number": self.route_number,
            # si close_date es datetime, lo convertimos a ISO; si ya es str, lo dejamos
            "close_date": self.close_date.isoformat()
                          if isinstance(self.close_date, datetime)
                          else self.close_date,
            "stops": self.stops,
            "cost": self.cost,
            "status": self.status
        }

    def to_json(self):
        """Devuelve un string JSON de la ruta."""
        return json.dumps(self.to_dict(), ensure_ascii=False)