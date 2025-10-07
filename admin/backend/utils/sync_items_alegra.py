import requests
from pymongo import MongoClient

# Conexión a la base de datos MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
products_collection = db['products']  # Suponiendo que los productos están en esta colección

# URL base y cabeceras para la API de Alegra
url_items = "https://api.alegra.com/api/v1/items"
headers = {
    "accept": "application/json",
    "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0",
    "content-type": "application/json"
}

# Función para obtener todos los productos de Alegra
def get_all_items():
    items = []
    start = 0
    limit = 30
    while True:
        response = requests.get(f"{url_items}?start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            items.extend(data)
            start += limit
        else:
            print(f"Error al obtener la lista de productos: {response.status_code} - {response.text}")
            break
    return items

def find_item_by_reference(items, reference):
    return next((item for item in items if item.get("reference") == reference), None)
# Función para crear un producto en la API de Alegra
def create_item_in_alegra(product):
    if product['unit'] == 'KG':
        unidad = 'kilogram'
    elif product['unit'] == 'UND':
        unidad = 'unit'
    else:
        unidad = 'unit'  # Valor por defecto si no coincide

    payload = {
        "type": "product",
        "name": product["name"],
        "reference": product["sku"],
        "price": product["price_sale"],
        "inventory": {
            "unit": unidad,
            "warehouses": [{"id": "1"}]
        }
    }

    response = requests.post(url_items, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Producto creado exitosamente: {response.json()}")
    else:
        print(f"Error al crear el producto: {response.status_code} - {response.text}")
def update_item_alegra(product):
    # Asignar la unidad según el valor de product['unit']
    if product['unit'] == 'KG':
        unidad = 'kilogram'
    elif product['unit'] == 'UND':
        unidad = 'unit'
    else:
        unidad = 'unit'  # Valor por defecto si no coincide

    payload = {
        "type": "product",
        "name": product["name"],
        "reference": product["sku"],
        "price": product["price_sale"],
        "inventory": {
            "unit": unidad,

            "warehouses": [{"id": "1"}]
        }
    }

    response = requests.put(url_items + '/' + str(product["id"]), headers=headers, json=payload)
    
    if response.status_code == 201:
        print(f"Producto actualizado exitosamente: {response.json()}")
    else:
        print(f"Error al actualizar el producto: {response.status_code} - {response.text}")


def sync_products():
    # Obtener todos los productos de la API de Alegra
    alegra_items = get_all_items()
    alegra_references = {item["reference"] for item in alegra_items}

    # Obtener todos los productos de la base de datos
    db_products = products_collection.find()
    for product in db_products:
        if product["sku"] not in alegra_references:
            print(f"Creando producto: {product['name']} ({product['sku']})")
            create_item_in_alegra(product)
        # else:
        #     alegra_product = find_item_by_reference(alegra_items,product['sku'])
        #     product["id"] = alegra_product["id"]
        #     update_item_alegra(product)            
        #     print(f"El producto {product['name']} ({product['sku']}) actualizado en Alegra")

sync_products()
