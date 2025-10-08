from flask import Blueprint, jsonify, request
from ..models.product import Product
import json
from flask_bcrypt import Bcrypt
from datetime import datetime
from decimal import Decimal
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
import json
from pymongo import MongoClient
from openpyxl import Workbook
import math
import requests
import csv
from io import StringIO
from flask import Response
import re
from io import BytesIO
product_api = Blueprint('product', __name__)

# Ruta para crear un nuevo product
@product_api.route('/product/', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')  
    price_sale = float(data.get('price_sale')) if data.get('price_sale') else 0
    price_purchase = float(data.get('price_purchase')) if data.get('price_purchase') else 0
    discount = float(data.get('discount')) if data.get('discount') else 0
    margen = float(data.get('margen')) if data.get('margen') else 0
    iva = data.get('iva').lower()  if bool(data.get('iva')) else False
    iva_value = float(data.get('iva_value')) if data.get('iva_value') else 0
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    quantity = data.get('quantity')
    step_unit = data.get('step_unit')
    root = data.get('root')
    child = data.get('child')
    step_unit_sipsa = data.get('step_unit_sipsa')
    factor_volumen = data.get('factor_volumen')
    sipsa_id = data.get('sipsa_id')
    last_price_purchase = data.get('price_purchase') 
    rate_root = 0
    is_visible = True
    tipo_pricing = data.get('tipo_pricing', 'Auto')
    proveedor = data.get('proveedor', None)
    if not sku or not name:
        return jsonify({'message': 'Missing required fields'}), 400

    if Product.find_by_sku(sku=sku):
        return jsonify({'message': 'Product already exists'}), 400

    product = Product(        
        name = name,
        unit = unit,
        category = category,
        sku = sku,
        price_sale = price_sale,
        price_purchase = price_purchase,
        discount = discount,
        margen = margen,
        iva = iva,
        iva_value = iva_value,
        description = description,
        image = image,
        status = status,
        quantity = quantity,
        step_unit_sipsa = step_unit_sipsa,
        step_unit = step_unit,
        factor_volumen = factor_volumen,
        sipsa_id = sipsa_id,
        last_price_purchase = last_price_purchase,
        proveedor= proveedor,
        rate_root = rate_root,
        root = root,
        child = child,
        is_visible = is_visible,
        tipo_pricing = tipo_pricing

    )
    product.save()
    return jsonify({'message': 'Product created successfully'}), 201

# Ruta para actualizar un usuario existente
@product_api.route('/products/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')
    price_sale = float(data.get('price_sale')) if data.get('price_sale') else None
    price_purchase = float(data.get('price_purchase')) if data.get('price_purchase') else None
    discount = float(data.get('discount')) if data.get('discount') else None
    margen = float(data.get('margen')) if data.get('margen') else None
    iva = data.get('iva').lower()  if data.get('iva') else None
    iva_value = float(data.get('iva_value')) if data.get('iva_value') else None
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    quantity = data.get('quantity')
    root   =   data.get('root')
    child   =  data.get('child')
    step_unit  = data.get('step_unit')
    last_price_purchase = data.get('last_price_purchase')
    proveedor = data.get('proveedor')
    rate_root = data.get('rate_root')
    is_visible = bool(data.get('is_visible'))
    factor_volumen = data.get('factor_volumen')
    product = Product.object(product_id)
    step_unit_sipsa = data.get('step_unit_sipsa')
    sipsa_id = data.get('sipsa_id')
    tipo_pricing = data.get('tipo_pricing', 'Auto')

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    product.id = product_id
    product.name = name or product.name
    product.unit = unit or product.unit
    product.category = category or product.category
    product.sku = sku or product.sku
    product.price_sale = price_sale if price_sale is not None else product.price_sale
    product.price_purchase = price_purchase if price_purchase is not None else product.price_purchase
    product.discount = discount if discount is not None else product.discount
    product.margen = margen if margen is not None else product.margen
    product.iva = iva or product.iva
    product.iva_value = iva_value if iva_value is not None else product.iva_value
    product.description = description or product.description
    product.image = image or product.image
    product.status = status or product.status
    product.quantity = quantity or product.quantity
    product.last_price_purchase = last_price_purchase or product.last_price_purchase
    product.root = root or product.root
    product.child = child or product.child
    product.step_unit = step_unit or product.step_unit
    product.proveedor = proveedor or product.proveedor
    product.rate_root = rate_root or product.rate_root
    product.is_visible = bool(is_visible) if is_visible is not None else bool(product.is_visible)
    product.factor_volumen = factor_volumen or product.factor_volumen
    product.step_unit_sipsa = step_unit_sipsa or product.step_unit_sipsa
    product.sipsa_id = sipsa_id or product.sipsa_id
    product.tipo_pricing = tipo_pricing or product.tipo_pricing
    product.updated()

    return jsonify({'message': 'Product updated successfully'}), 200

@product_api.route('/products/', methods=['GET'])
def list_product():
    # Filtrar solo los productos con status "active"
    products_cursor = Product.objects(status="active")

    # Construir los datos del producto para la respuesta JSON
    product_data = [
        {
            "id": str(product["_id"]), 
            "name": product["name"], 
            "unit": product["unit"], 
            "category": product["category"], 
            "sku": product["sku"], 
            "price_sale": product["price_sale"], 
            "price_purchase": product["price_purchase"], 
            "discount": product["discount"], 
            "margen": product["margen"], 
            "iva": product["iva"], 
            "iva_value": product["iva_value"], 
            "description": product["description"], 
            "image": product["image"], 
            "status": product["status"],
            "quantity" : product["quantity"],
            "step_unit" :  product["step_unit"],
            "step_unit_sipsa" :  product["step_unit_sipsa"],
            "factor_volumen" : product["factor_volumen"],
            "sipsa_id" : product["sipsa_id"],
            "root" : product["root"],
            "child" : product["child"],
            "last_price_purchase" : product["last_price_purchase"],
            "is_visible" : product["is_visible"],
            "tipo_pricing": product["tipo_pricing"],
            "proveedor" : product["proveedor"],
        }
        for product in products_cursor
    ]

    # Convertir los datos del producto a formato JSON
    products_json = json.dumps(product_data)

    # Devolver la respuesta JSON con el código de estado 200 (OK)
    return products_json, 200

@product_api.route('/products_customer/<string:customer_email>', methods=['GET'])
def list_product_customer(customer_email):
    # Filtrar solo los productos con status "active"
    products_cursor = Product.objects_customer(customer_email=customer_email)

    # Construir los datos del producto para la respuesta JSON
    product_data = [
        {
            "id": str(product["_id"]), 
            "name": product["name"], 
            "unit": product["unit"], 
            "category": product["category"], 
            "sku": product["sku"], 
            "price_sale": product["price_sale"], 
            "price_purchase": product["price_purchase"], 
            "discount": product["discount"], 
            "margen": product["margen"], 
            "iva": product["iva"], 
            "iva_value": product["iva_value"], 
            "description": product["description"], 
            "image": product["image"], 
            "status": product["status"],
            "quantity" : product["quantity"],
            "root" : product["root"],
            "child" : product["child"],
            "proveedor" : product["proveedor"],
            "step_unit" : product["step_unit"],
            "rate_root" : product["rate_root"],
        }
        for product in products_cursor
    ]

    # Convertir los datos del producto a formato JSON
    products_json = json.dumps(product_data)

    # Devolver la respuesta JSON con el código de estado 200 (OK)
    return products_json, 200

@product_api.route('/syn_products_page', methods=['GET'])
def syn_products_page():
    consumer_key = 'ck_4bf46790d37d0d9b58d0412564c8be7431496ef1'
    consumer_secret = 'cs_a638277a5fc58e9c8c98a23e6efc88a51ae91fb7'
    base_url = 'https://www.buyfrescapp.com/wp-json/wc/v3/products'

    # Conexión a MongoDB
    client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
    db = client['frescapp']
    collection = db['products']

    # Obtener IDs de todos los productos existentes para eliminar
    product_ids = []
    for page in range(1, 5):  # Iterar sobre las páginas
        url = f'{base_url}?consumer_key={consumer_key}&consumer_secret={consumer_secret}&per_page=100&page={page}'
        response = requests.get(url)
        if response.status_code == 200:
            products = response.json()
            if not products:  # Detenerse si no hay más productos
                break
            product_ids.extend([product['id'] for product in products])  # Agregar IDs al arreglo
        else:
            print(f"Error al obtener productos de WooCommerce en la página {page}: {response.status_code}")
            break

    print(f"Se encontraron {len(product_ids)} productos para eliminar.")
    # Preparar productos para crear desde MongoDB
    products_to_create = []
    mongo_products = collection.find({"is_visible": True})  # Consultar todos los productos en MongoDB
    for product in mongo_products:
        categoria_id = "0"
        if product["category"] == 'Hotalizas':
            categoria_id = "16"
        if product["category"] == 'Tubérculos':
            categoria_id = "43"
        if product["category"] == 'Frutas':
            categoria_id = "32"
        if product["category"] == 'Verduras':
            categoria_id = "33"
        if product["category"] == 'Abarrotes':
            categoria_id = 44
        producto = {
            "name": product["name"],
            "sku": product["sku"],
            "sale_price": str(product["price_sale"]),
            "price": str(product["price_sale"]),
            "regular_price": str(product["price_sale"]),
            "categories": [{"id": categoria_id, "name": product["category"]}],
            "tags": [{"name": product["unit"]}],
            "images": [{"src": product["image"]}]
        }
        products_to_create.append(producto)

    print(f"Se prepararon {len(products_to_create)} productos para crear.")

    # Dividir en lotes y procesar batch (eliminar y crear)
    batch_size = 100
    total_batches = math.ceil(len(product_ids) / batch_size)
    created_batches = math.ceil(len(products_to_create) / batch_size)

    # Eliminar en lotes
    for batch_index in range(total_batches):
        start = batch_index * batch_size
        end = start + batch_size
        batch = product_ids[start:end]
        
        # Endpoint de actualización batch
        url_update = f'{base_url}/batch?consumer_key={consumer_key}&consumer_secret={consumer_secret}'
        payload = {"delete": batch}  # Preparar datos para batch delete
        response = requests.post(url_update, json=payload)
        
        if response.status_code == 200:
            print(f"Lote {batch_index + 1} de {total_batches} eliminado correctamente.")
        else:
            print(f"Error al eliminar el lote {batch_index + 1}: {response.status_code}, {response.text}")

    # Crear productos en lotes
    for product_to_create in products_to_create:
        url_update = f'{base_url}?consumer_key={consumer_key}&consumer_secret={consumer_secret}'
        response = requests.post(url_update, json=product_to_create)
        #print(product_to_create["sku"] + " - "+str(response.status_code))
    return f"Creado exitosamente", 200
    
@product_api.route('/product/institucion/', defaults={'email': None}, methods=['GET'])
@product_api.route('/product/institucion/<string:email>', methods=['GET'])
def list_product_institucion(email):
    def generate_excel(email):
        def limpiar_sku(sku):
            return re.sub(r'[^A-Za-z0-9\-]', '', sku)

        client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
        db = client['frescapp']
        customers_collection = db['customers']

        wb = Workbook()
        ws = wb.active
        ws.title = "Productos"
        ws.append(["Nombre", "Unidad", "Categoria", "Precio","SKU"])

        if not email:
            for p in Product.objects('active'):
                nombre = p.get("name", "Sin nombre")
                step = p.get("step_unit", 1)
                categoria = p.get("category", "Sin categoria")
                unidad = p.get("unit", "Sin unidad")
                precio_base = p.get("price_sale", 0) * step
                precio_descuento = int(round(precio_base * 0.88))
                ws.append([nombre, unidad, categoria, precio_descuento])
        else:
            customer = customers_collection.find_one({'email': email})
            if not customer or 'match_catalogo' not in customer:
                return wb

            match_catalogo = []
            sku_list = []

            for item in customer['match_catalogo']:
                sku = limpiar_sku(item.get('sku', ''))
                if sku:
                    match_catalogo.append({
                        "sku": sku,
                        "name": item.get("equivalente", "Sin nombre"),
                        "step_unit": item.get("step_unit", 1)
                    })
                    sku_list.append(sku)

            productos_encontrados = {p["sku"]: p for p in Product.find_by_skus(sku_list)}

            for item in match_catalogo:
                sku = item["sku"]
                nombre = item["name"]
                step = item["step_unit"]

                if sku in productos_encontrados:
                    product = productos_encontrados[sku]
                    precio_base = product["price_sale"] * step
                    precio_descuento = int(round(precio_base * 0.84))
                    unidad = product.get("unit", "Sin unidad")
                    categoria = product.get("category", "Sin categoria")
                else:
                    precio_descuento = ""
                    unidad = ""
                    categoria = ""

                ws.append([nombre, unidad, categoria, precio_descuento,sku])

        return wb

    wb = generate_excel(email)
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return Response(
        output.read(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=productos_institucion.xlsx"}
    )