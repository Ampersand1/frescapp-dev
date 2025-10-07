from pymongo import MongoClient
from collections import Counter

# Configuración de la conexión
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
orders_collection = db['orders']
customers_collection = db['customers']

def actualizar_productos_mas_vendidos():
    # Iterar sobre cada cliente en la colección 'customers'
    for customer in customers_collection.find():
        customer_email = customer.get('email')
        if not customer_email:
            continue  # Saltar si no hay correo electrónico

        # Obtener los productos comprados por el cliente desde la colección 'orders'
        orders = orders_collection.find({'customer_email': customer_email}, {'products.sku': 1})
        skus = [product['sku'] for order in orders for product in order.get('products', [])]

        # Contar la frecuencia de cada SKU
        sku_counter = Counter(skus)
        top_skus = [sku for sku, _ in sku_counter.most_common(20)]

        # Actualizar el atributo 'list_products' del cliente con los SKUs más vendidos
        customers_collection.update_one(
            {'_id': customer['_id']},
            {'$set': {'list_products': top_skus}}
        )
        print(f"Actualizado {customer_email} con los productos más vendidos.")

if __name__ == '__main__':
    actualizar_productos_mas_vendidos()
