from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
products_collection = db['products_history']  

class ProductHistory:
    def __init__(self, 
                 operation_date,
                 name, 
                 unit, 
                 category, 
                 sku, 
                 root,
                 child,
                 step_unit,
                 step_unit_sipsa,
                 factor_volumen,
                 margen,
                 last_price_purchased,
                 minimokg,
                 maximokg,
                 promediokg,
                 price_sale, 
                 price_purchase,
                 last_price_purchase,
                 last_price_sale,
                 sipsa_id
                 ):
        self.operation_date = operation_date
        self.name = name
        self.unit = unit
        self.category = category
        self.sku = sku
        self.root = root
        self.child = child
        self.step_unit = step_unit
        self.step_unit_sipsa = step_unit_sipsa
        self.margen = margen
        self.last_price_purchased = last_price_purchased
        self.minimokg = minimokg
        self.maximokg = maximokg
        self.promediokg = promediokg
        self.price_sale = price_sale
        self.price_purchase = price_purchase
        self.last_price_purchase = last_price_purchase
        self.last_price_sale = last_price_sale
        self.factor_volumen = factor_volumen
        self.sipsa_id = sipsa_id

    def save(self):
        product_data = {
            "operation_date": self.operation_date,
            "name": self.name,
            "unit": self.unit,
            "category": self.category,
            "sku": self.sku,
            "root": self.root,
            "child" : self.child,
            "step_unit" : self.step_unit,
            "step_unit_sipsa" : self.step_unit_sipsa,
            "margen" : self.margen,
            "last_price_purchased" : self.last_price_purchased,
            "minimoKg" : self.minimokg,
            "maximoKg" : self.maximokg,
            "promedioKg" : self.promediokg,
            "price_sale" : self.price_sale,
            "price_purchase" : self.price_purchase,
            "last_price_purchase" : self.last_price_purchase,
            "last_price_sale" : self.last_price_sale,
            "factor_volumen" : self.factor_volumen,
            "sipsa_id" : self.sipsa_id
        }
        result = products_collection.insert_one(product_data)
        return result.inserted_id
    
    def updated(self):
        products_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": { 
                        "operation_date": self.operation_date,
                        "name": self.name,
                        "unit": self.unit,
                        "category": self.category,
                        "sku": self.sku,
                        "root": self.root,
                        "child" : self.child,
                        "step_unit" : self.step_unit,
                        "step_unit_sipsa" : self.step_unit_sipsa,
                        "margen" : self.margen,
                        "last_price_purchased" : self.last_price_purchased,
                        "minimoKg" : self.minimokg,
                        "maximoKg" : self.maximokg,
                        "promedioKg" : self.promediokg,
                        "price_sale" : self.price_sale,
                        "price_purchase" : self.price_purchase,
                        "last_price_purchase" : self.last_price_purchase,
                        "last_price_sale" : self.last_price_sale,
                        "factor_volumen" : self.factor_volumen,
                        "sipsa_id" : self.sipsa_id
                    }
            }
        )
    @staticmethod
    def objects(fecha_inicio: str, fecha_fin: str):        
        # Consulta en el rango de fechas
        return products_collection.find({
            "operation_date": {
                "$gte": fecha_inicio,
                "$lte": fecha_fin
            }
        })

    @staticmethod
    def object(id):
        product_data = products_collection.find_one({'_id': ObjectId(id) }, {'_id': 0})
        if product_data:
            return ProductHistory(**product_data)
        else:
            return None