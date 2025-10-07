from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
products_collection = db['products']  
customers_collection = db['customers']  

class Product:
    def __init__(self, 
                 name, 
                 unit, 
                 category, 
                 sku, 
                 price_sale, 
                 price_purchase, 
                 discount, 
                 margen,
                 iva,
                 iva_value,
                 description,
                 image,
                 status,
                 root,
                 child,
                 step_unit,
                 step_unit_sipsa,
                 factor_volumen,
                 sipsa_id,
                 proveedor,
                 rate_root,
                 last_price_purchase,
                 quantity,
                 is_visible,
                 tipo_pricing):
        self.name = name
        self.unit = unit
        self.category = category
        self.sku = sku
        self.price_sale = price_sale
        self.price_purchase = price_purchase
        self.discount = discount
        self.margen = margen
        self.iva = iva
        self.iva_value = iva_value
        self.description = description
        self.image = image
        self.status = status
        self.root = root
        self.child = child
        self.step_unit = step_unit
        self.proveedor = proveedor
        self.rate_root = rate_root
        self.step_unit_sipsa = step_unit_sipsa
        self.factor_volumen = factor_volumen
        self.sipsa_id = sipsa_id
        self.last_price_purchase = last_price_purchase
        self.quantity = quantity
        self.is_visible = is_visible
        self.tipo_pricing = tipo_pricing

    def save(self):
        product_data = {
            "name": self.name,
            "unit": self.unit,
            "category": self.category,
            "sku": self.sku,
            "price_sale": self.price_sale,
            "price_purchase": self.price_purchase,
            "discount" : self.discount,
            "margen" : self.margen,
            "iva" : self.iva,
            "iva_value" : self.iva_value,
            "description" : self.description,
            "image" : self.image,
            "status" : self.status,
            "step_unit_sipsa" : self.step_unit_sipsa,
            "factor_volumen" : self.factor_volumen,
            "sipsa_id" : self.sipsa_id,
            "last_price_purchase" : self.last_price_purchase,
            "quantity" : int(self.quantity),
            "root":self.root,
            "child": self.child,
            "step_unit":self.step_unit,
            "proveedor" : self.proveedor,
            "rate_root" : self.rate_root,
            "is_visible" : self.is_visible,
            "tipo_pricing": self.tipo_pricing
        }
        result = products_collection.insert_one(product_data)
        return result.inserted_id
    
    def updated(self):
        products_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": { 
                        "name": self.name,
                        "unit": self.unit,
                        "category": self.category,
                        "sku": self.sku,
                        "price_sale": self.price_sale,
                        "price_purchase": self.price_purchase,
                        "discount" : self.discount,
                        "margen" : self.margen,
                        "iva" : self.iva,
                        "iva_value" : self.iva_value,
                        "description" : self.description,
                        "image" : self.image,
                        "status" : self.status,
                        "step_unit_sipsa" : self.step_unit_sipsa,
                        "factor_volumen" : self.factor_volumen,
                        "sipsa_id" : self.sipsa_id,
                        "last_price_purchase" : self.last_price_purchase,
                        "quantity" : self.quantity,
                        "root":self.root,
                        "child": self.child,
                        "step_unit":self.step_unit,
                        "proveedor" : self.proveedor,
                        "rate_root" : self.rate_root,
                        "is_visible" : bool(self.is_visible),
                        "factor_volumen" : self.factor_volumen,
                        "tipo_pricing": self.tipo_pricing
                    }
            }
        )
    

    @staticmethod
    def objects(status=None):
        if status is not None:
            return products_collection.find({"status": status})
        return products_collection.find()

    @staticmethod
    def objects_customer( customer_email):
        if customer_email == 'undefined':
            customer_product_skus = ['BOG-CAT003-00029','BOG-CAT001-00002','BOG-CAT001-00007','BOG-CAT001-00004','BOG-CAT002-00001','BOG-CAT001-00005',
'BOG-CAT004-00001','BOG-CAT004-00003','BOG-CAT001-00001','BOG-CAT001-00003','BOG-CAT001-00006','BOG-CAT001-00013','BOG-CAT004-00011',
'BOG-CAT001-00017','BOG-CAT001-00008','BOG-CAT003-00005','BOG-CAT002-00007','BOG-CAT004-00004','BOG-CAT003-00003','BOG-CAT001-00015',
'BOG-CAT001-00020','BOG-CAT004-00024','BOG-CAT002-00008','BOG-CAT001-00042','BOG-CAT002-00004','BOG-CAT001-00057','BOG-CAT001-00014',
'BOG-CAT002-00036','BOG-CAT004-00006','BOG-CAT002-00002','BOG-CAT001-00009']
        else:
            customer = customers_collection.find_one({"email": customer_email})
            customer_product_skus = customer.get('list_products', [])
        
        all_active_products = list(products_collection.find({"is_visible": True}))
        
        product_dict = {product['sku']: product for product in all_active_products}
        ordered_products = []
        for product_sku in customer_product_skus:
            print(f"Checking product {product_sku}")
            if product_sku in product_dict:
                try:
                    print(f"Processing product {product_sku}")
                    ordered_products.append(product_dict.pop(product_sku))
                except Exception as e:
                    print(f"Error processing product {product_sku}: {e}")
        
        remaining_products = list(product_dict.values())
        ordered_products.extend(remaining_products)
        
        return ordered_products

    @staticmethod
    def object(id):
        product_data = products_collection.find_one({'_id': ObjectId(id) }, {'_id': 0})
        if product_data:
            return Product(**product_data)
        else:
            return None
    @staticmethod
    def find_by_sku(sku):
        return products_collection.find_one({"sku": sku},  {'_id': 0})
    @staticmethod
    def find_by_skus(sku_list):
        return products_collection.find(
            {"sku": {"$in": sku_list}},
            {'_id': 0}
        )
