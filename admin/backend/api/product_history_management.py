from flask import Blueprint, jsonify, request
from ..models.product_history import ProductHistory
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime
from decimal import Decimal
import pandas as pd
import os, math
import json, requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import time

product_history_api = Blueprint('products_history', __name__)

@product_history_api.route('/products_history/<string:operation_date_start>/<string:operation_date_end>', methods=['GET'])
def list_products_history(operation_date_start,operation_date_end):
    products_cursor = ProductHistory.objects(operation_date_start,operation_date_end)
    product_data = [
        {
            "id": str(product["_id"]), 
            "operation_date": product["operation_date"],
            "name": product["name"],
            "unit": product["unit"],
            "category": product["category"],
            "sku": product["sku"],
            "root": product["root"],
            "child" : product["child"],
            "step_unit" : product["step_unit"],
            "step_unit_sipsa" : product["step_unit_sipsa"],
            "margen" : product["margen"],
            "last_price_purchased" : product["last_price_purchased"],
            "minimoKg" : product["minimoKg"],
            "maximoKg" : product["maximoKg"],
            "promedioKg" : product["promedioKg"],
            "price_sale" : product["price_sale"],
            "price_purchase" : product["price_purchase"],
            "last_price_purchase" : product["last_price_purchase"],
            "last_price_sale" : product["last_price_sale"],
            "factor_volumen" : product["factor_volumen"],
            "sipsa_id" : product["sipsa_id"]
        }
        for product in products_cursor
    ]
    products_json = json.dumps(product_data)
    return products_json, 200

@product_history_api.route('/products_history_analytics', methods=['GET'])
def products_history_analytics():
    # Fechas necesarias
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    last_tuesday = today - timedelta(days=today.weekday() + 6)  # El martes de la semana pasada

    # Consultas a la base de datos
    products_today = ProductHistory.objects(today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
    products_yesterday = ProductHistory.objects(yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"))
    products_last_tuesday = ProductHistory.objects(last_tuesday.strftime("%Y-%m-%d"), last_tuesday.strftime("%Y-%m-%d"))

    # Convertir resultados en diccionarios para facilitar el acceso por SKU
    products_today_dict = {product["sku"]: product for product in products_today}
    products_yesterday_dict = {product["sku"]: product for product in products_yesterday}
    products_last_tuesday_dict = {product["sku"]: product for product in products_last_tuesday}

    # Generar datos enriquecidos con variaciones porcentuales
    product_data = []
    for sku, product_today in products_today_dict.items():
        yesterday_price = products_yesterday_dict.get(sku, {}).get("price_sale", None)
        last_tuesday_price = products_last_tuesday_dict.get(sku, {}).get("price_sale", None)

        variation_yesterday_today = (
            round(((product_today["price_sale"] - yesterday_price) / yesterday_price * 100), 1)
            if yesterday_price else None
        )
        variation_last_week_today = (
            round(((product_today["price_sale"] - last_tuesday_price) / last_tuesday_price * 100), 1)
            if last_tuesday_price else None
        )

        product_data.append({
            "id": str(product_today["_id"]),
            "name": product_today["name"],
            "unit": product_today["unit"],
            "sku": product_today["sku"],
            "price_sale_today": round(product_today["price_sale"], 1) if product_today["price_sale"] else None,
            "price_sale_yesterday": round(yesterday_price, 1) if yesterday_price else None,
            "price_sale_last_tuesday": round(last_tuesday_price, 1) if last_tuesday_price else None,
            "variation_yesterday_today": variation_yesterday_today,
            "variation_last_week_today": variation_last_week_today,
        })

    # Convertir a JSON y retornar
    products_json = json.dumps(product_data)
    return products_json, 200

@product_history_api.route('/products_history_new/<string:operation_date>', methods=['GET'])
def products_history_new(operation_date):
    def obtenerSipsa(operation_date:str,path_destino: str):
        operation_date = (datetime.strptime(operation_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"Obteniendo datos de SIPSA para la fecha: {operation_date}")
        url = "https://apps.dane.gov.co/pentaho/plugin/cda/api/doQuery"
        timeout = 120 
        # Cabeceras HTTP para la primera solicitud
        headers = {
            "Accept": "text/plain, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,pt;q=0.6",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Cookie": "JSESSIONID=90A80A2BECD016F382835714656B1775; session-flushed=true; cookiesession1=678B769F8ACECBBC074156C4D45B1560; _ga=GA1.1.159507109.1730395042; PRETSESSID=4kk7sl6ifmi42v7i5n1qi4oqg122rv6k; _ga_T3L41X6043=GS1.1.1730735072.1.1.1730735938.60.0.0; _ga_BM7WT3EVCG=GS1.1.1730735072.1.1.1730735938.0.0.0; _ga_6WXKXLP4PK=GS1.1.1730735072.1.1.1730735938.0.0.0; _clck=1j7zqxe%7C2%7Cfqm%7C0%7C1765; _ga_MV4DN0WN4F=GS1.1.1730842549.10.1.1730843698.0.0.0; _ga_EVNW3DW2NE=GS1.1.1730842549.10.1.1730843698.60.0.2002533807",
            "Host": "apps.dane.gov.co",
            "Origin": "https://apps.dane.gov.co",
            "Referer": "https://apps.dane.gov.co/pentaho/api/repos/%3Apublic%3ASIPSA%3ASIPSAV17.wcdf/generatedContent",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }

        # Parámetros de la primera solicitud
        payload = {
            "parampardPeriodoIni": operation_date,
            "parampardPeriodoFin": operation_date,
            "paramparcArticulo": [
                'Acelga', 'Aguacate Hass', 'Aguacate papelillo', 'Ahuyama', 'Ahuyamín (Sakata)', 
                'Ajo', 'Ajo importado', 'Apio', 'Arracacha amarilla', 'Arveja verde en vaina', 
                'Arveja verde en vaina pastusa', 'Banano bocadillo', 'Banano criollo', 'Banano Urabá', 
                'Berenjena', 'Borojó', 'Brócoli', 'Calabacín', 'Calabaza', 'Cebolla cabezona blanca', 
                'Cebolla cabezona roja', 'Cebolla junca Aquitania', 'Chócolo mazorca', 'Cidra', 'Cilantro',
                'Ciruela importada', 'Ciruela roja', 'Coco', 'Coliflor', 'Curuba', 'Durazno nacional',
                'Espinaca', 'Fresa', 'Fríjol verde cargamanto', 'Granadilla', 'Guanábana', 'Guayaba pera',
                'Gulupa', 'Habichuela', 'Kiwi', 'Lechuga Batavia', 'Lechuga crespa verde', 'Limón común',
                'Limón Tahití', 'Lulo', 'Mandarina Arrayana', 'Mango Tommy', 'Manzana nacional', 
                'Manzana roja importada', 'Manzana royal gala importada', 'Manzana verde importada', 
                'Maracuyá', 'Melón Cantalup', 'Mora de Castilla', 'Naranja Sweet', 'Naranja Valencia', 
                'Papa criolla limpia', 'Papa criolla sucia', 'Papa parda pastusa', 'Papa rubí', 'Papa R-12 negra', 
                'Papa R-12 roja', 'Papa sabanera', 'Papa superior', 'Papa única', 'Papaya Paulina', 
                'Papaya tainung', 'Patilla', 'Patilla baby', 'Pepino cohombro', 'Pepino de rellenar', 
                'Pera importada', 'Pera nacional', 'Perejil', 'Pimentón', 'Piña gold', 'Piña perolera', 
                'Pitahaya', 'Plátano guineo', 'Plátano hartón maduro', 'Plátano hartón verde', 
                'Plátano hartón verde llanero', 'Rábano rojo', 'Remolacha', 'Repollo morado', 
                'Repollo verde', 'Tangelo', 'Tomate chonto', 'Tomate de árbol', 'Tomate larga vida', 
                'Uchuva con cáscara', 'Uva importada', 'Uva Isabela', 'Uva red globe nacional', 
                'Uva verde', 'Yuca llanera', 'Zanahoria', 'Cebolla puerro'
            ],
            "paramparsPrecio": "Diario",
            "paramparcFuente": "Bogotá, D.C., Corabastos",
            "path": "/public/SIPSA/SIPSAV17.cda",
            "dataAccessId": "qryTabla",
            "outputIndexId": "1",
            "pageSize": "0",
            "pageStart": "0",
            "sortBy": "", 
            "paramsearchBox":"", 
            "outputType": "xls",
            "settingattachmentName": "sipsaexporta.xls",
            "wrapItUp": "true"
        }
        # Realizar la primera solicitud POST para obtener el uuid
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            uuid = response.text  # Ajustar según el formato exacto de la respuesta si es necesario
            # Realizar la segunda solicitud GET usando el uuid
            url_get = f"https://apps.dane.gov.co/pentaho/plugin/cda/api/unwrapQuery?path=%2Fpublic%2FSIPSA%2FSIPSAV17.cda&uuid={uuid}"
            
            # Cabeceras de la segunda solicitud
            headers_get = headers.copy()
            headers_get.update({
                'Sec-Fetch-Dest': 'iframe',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            })

            # Realizar la solicitud GET para descargar el archivo
            response_get = requests.get(url_get, headers=headers_get)
            if response_get.status_code == 200:
                # Guardar el contenido como un archivo Excel
                with open(path_destino, 'wb') as file:
                    file.write(response_get.content)
                print("Archivo descargado exitosamente.")
                return True
            else:
                print(f"Error al realizar la solicitud GET: {response_get.status_code}")
                return False
        else:
            print(f"Error en la primera solicitud: {response.status_code}")
            return False

    def extractDataFromExcel(filepath: str, filter_date: str) -> object:
        # Lee el archivo Excel
        data = pd.read_excel(filepath)

        # Asegúrate de que la columna de fecha esté en formato datetime para compararla
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')

        # Convierte el parámetro filter_date a datetime y réstale un día
        filter_date = datetime.strptime(filter_date, '%Y-%m-%d') - timedelta(days=1)

        # Filtra los registros que coincidan con la fecha ajustada
        filtered_data = data[data['FECHA'] == filter_date]

        # Estructura los datos filtrados en una lista de diccionarios
        records = filtered_data.to_dict(orient='records')
        return records

    def precio_familia_compra(uri: str, db_name: str, sku: str, operation_date: str):
        client = MongoClient(uri)
        db = client[db_name]
        exclusion = {"_id": 0, "image": 0, "description": 0}
        
        sku_padre = db["products"].find_one(
            {"status": "active", "sku": sku},
            exclusion
        )
        sku_padre = sku_padre.get('child')
        productos_activos = db["products"].find(
            {"status": "active", "$or": [{"sku": sku_padre}, {"child": sku_padre}]},
            exclusion
        )
        
        # Convertimos el cursor a una lista para iterarlo después de imprimir
        productos_lista = list(productos_activos)
        total_precio = 0
        contador = 0
        
        # Itera sobre cada producto activo
        for producto in productos_lista:
            sku_familia = producto.get("sku")
            
            # Encuentra la compra más reciente de este SKU
            compras = db["purchases"].find_one(
                {
                    "date": operation_date,
                    "products.sku": sku_familia
                },
                {"products.$": 1}
            )
            
            if compras:
                producto_encontrado = compras["products"][0]
                precio_compra = float(producto_encontrado.get("final_price_purchase", 0) or 0)
                step_unit = float(producto.get("step_unit", 1)) 
                total_precio += precio_compra / step_unit
                
                contador += 1

        client.close()
        return total_precio / contador if contador > 0 else 0

    def safe_round(value):
        try:
            return round(float(value))
        except (TypeError, ValueError):
            return 0

    def copiar_productos_activos_y_actualizar(uri: str, db_name: str, coleccion_origen: str, coleccion_destino: str, operation_date: str, equivalence_data: list):
        client = MongoClient(uri)
        db = client[db_name]

        exclusion = {"_id": 0, "image": 0, "description": 0}
        productos_activos = db[coleccion_origen].find({"status": "active"}, exclusion)
        def safe_float(value, default=1.0):
            try:
                return float(value) if value not in [None, '', 'null'] else default
            except (ValueError, TypeError):
                return default
        for producto in productos_activos:
            # Asegura que no tenga _id
            producto.pop("_id", None)

            sku = producto.get("sku")
            precio_compra_dia = precio_familia_compra(uri, db_name, sku, operation_date)

            equivalence_match = next(
                (
                    item for item in equivalence_data
                    if str(item.get('ARTICULO')) == str(producto.get("sipsa_id")) 
                    and (pd.to_datetime(item.get('FECHA'), errors='coerce') + timedelta(days=1)) == pd.to_datetime(operation_date)
                ),
                None
            )

            step_unit_sipsa = safe_float(producto.get("step_unit_sipsa"))
            step_unit = float(producto.get("step_unit", 1))
            factor_volumen = float(producto.get("factor_volumen", 1))
            margen = float(producto.get("margen", 0))

            minimoKg = safe_round(float(equivalence_match["MINIMO"]) * step_unit_sipsa) if equivalence_match else 0
            maximoKg = safe_round(float(equivalence_match["MAXIMO"]) * step_unit_sipsa) if equivalence_match else 0
            promedioKg = safe_round(float(equivalence_match["PROMEDIO"]) * step_unit_sipsa) if equivalence_match else 0
            if producto.get("tipo_pricing") == "Auto":
                if precio_compra_dia:
                    price_purchase = precio_compra_dia * step_unit
                elif promedioKg:
                    price_purchase = maximoKg
                else:
                    price_purchase = float(producto.get("price_purchase", 0))
            else:
                price_purchase = float(producto.get("price_purchase", 0))

            price_purchase *= factor_volumen
            price_sale = price_purchase * (1 + margen)

            producto.update({
                "operation_date": operation_date,
                "last_price_purchased": safe_round(precio_compra_dia),
                "minimoKg": minimoKg,
                "maximoKg": maximoKg,
                "promedioKg": promedioKg,
                "price_purchase": safe_round(price_purchase),
                "price_sale": safe_round(price_sale),
                "last_price_purchase": safe_round(producto.get("price_purchase", 0)),
                "last_price_sale": safe_round(producto.get("price_sale", 0))
            })

            try:
                db[coleccion_destino].insert_one(producto)
            except Exception as e:
                print(f"Error insertando producto con SKU {sku}: {e}")

        client.close()
        print("Productos actualizados y copiados exitosamente.")

    def actualizar_precios_en_products(uri: str, db_name: str, coleccion_origen: str, operation_date: str):
        client = MongoClient(uri)
        db = client[db_name]

        # Obtiene los productos de products_history según la operation_date
        productos_history = db[coleccion_origen].find({"operation_date": operation_date})
        
        for producto_hist in productos_history:
            # Busca el producto en products por sku
            sku = producto_hist.get("sku")
            if not sku:
                continue  # Si no tiene SKU, pasa al siguiente producto

            # Actualiza los campos price_sale y price_purchase en products
            db["products"].update_one(
                {"sku": sku},
                {"$set": {
                    "price_purchase": producto_hist.get("price_purchase"),
                    "price_sale": producto_hist.get("price_sale")
                }}
            )

        client.close()
        print("Precios actualizados en la colección 'products'.")

    def delete_product_history(operation_date:str):
        uri = 'mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp'
        client = MongoClient(uri)
        db = client["frescapp"]
        coleccion_historial = db["products_history"]
        coleccion_historial.delete_many({"operation_date": operation_date})
        client.close()
    def update_price_page():
        consumer_key = 'ck_203177d4d7a291000f60cd669ab7cb98976b3620'
        consumer_secret = 'cs_d660a52cd323666cad9b600a9d61ed6c577cd6f9'
        base_url = 'https://www.buyfrescapp.com/wp-json/wc/v3/products'
        # Conexión a MongoDB
        client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
        db = client['frescapp']
        collection = db['products']
        woo_products = []
        for page in range(1, 5):  # Iterar tres páginas
            url = f'{base_url}?consumer_key={consumer_key}&consumer_secret={consumer_secret}&per_page=100&page={page}'
            response = requests.get(url)
            if response.status_code == 200:
                woo_products.extend(response.json())
            else:
                print(f"Error al obtener productos de WooCommerce en la página {page}: {response.status_code}")
                break

            # Obtener productos de MongoDB
            mongo_products = list(collection.find({"status": "active"}, {"name": 1, "sku": 1, "price_sale": 1, "category": 1}))

            # Hacer el emparejamiento por SKU
            matched_products = []
            for woo_product in woo_products:
                woo_sku = woo_product.get("sku")
                if woo_sku:
                    # Buscar el producto en MongoDB por SKU
                    mongo_product = next((prod for prod in mongo_products if prod.get("sku") == woo_sku), None)
                    if mongo_product:
                        matched_products.append({
                            "id": woo_product.get("id"),
                            "name": mongo_product.get("name"),
                            "sku": mongo_product.get("sku"),
                            "sale_price": mongo_product.get("price_sale"),
                            "price": mongo_product.get("price_sale"),
                            "regular_price": mongo_product.get("price_sale")
                        })
            # Enviar productos en lotes de 100
            batch_size = 100
            total_batches = math.ceil(len(matched_products) / batch_size)

            for batch_index in range(total_batches):
                start = batch_index * batch_size
                end = start + batch_size
                batch = matched_products[start:end]
            
            # Endpoint de actualización batch
            url_update = f'{base_url}/batch?consumer_key={consumer_key}&consumer_secret={consumer_secret}'
            actualizacion = requests.post(url_update, json={"update": batch})

    
    uri = 'mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp'
    db_name = "frescapp"
    coleccion_origen = "products"
    coleccion_destino = "products_history"
    fields = ['ARTICULO', 'PROMEDIO', 'MINIMO', 'MAXIMO', 'FECHA', 'FUENTE']
    filepath = os.path.join(os.path.dirname(__file__), f"sipsaexporta_{operation_date}.xls")


    sipsa = obtenerSipsa(operation_date,filepath)
    delete_product_history(operation_date)
    print("Historial de productos eliminado.")
    if sipsa:
        data = extractDataFromExcel(filepath, operation_date)
    else:
        data = []
    copiar_productos_activos_y_actualizar(uri, db_name, coleccion_origen, coleccion_destino, operation_date, data)
    actualizar_precios_en_products(uri, db_name, coleccion_destino, operation_date)
    update_price_page()
    # if os.path.exists(filepath):
    #     os.remove(filepath)
    return jsonify({"message": "Productos actualizados."}),  200