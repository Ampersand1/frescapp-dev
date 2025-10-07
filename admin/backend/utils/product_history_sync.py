from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import requests, os
import json

def obtenerSipsa(operation_date:str,path_destino: str):
        # URL de la API para obtener el uuid
    url = "https://apps.dane.gov.co/pentaho/plugin/cda/api/doQuery"

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
        else:
            print(f"Error al realizar la solicitud GET: {response_get.status_code}")
    else:
        print(f"Error en la primera solicitud: {response.status_code}")

def extractDataFromExcel(filepath: str, filter_date: str) -> object:
    # Lee el archivo Excel
    data = pd.read_excel(filepath)

    # Asegúrate de que la columna de fecha esté en formato datetime para compararla
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')

    # Convierte el parámetro filter_date a un objeto datetime
    filter_date = datetime.strptime(filter_date, '%Y-%m-%d')

    # Filtra los registros que coincidan con la fecha especificada
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
            precio_compra = float(producto_encontrado.get("final_price_purchase", 0))
            step_unit = float(producto.get("step_unit", 1)) 
            total_precio += precio_compra / step_unit
            
            contador += 1

    client.close()
    return total_precio / contador if contador > 0 else 0

def copiar_productos_activos_y_actualizar(uri: str, db_name: str, coleccion_origen: str, coleccion_destino: str, operation_date: str, equivalence_data: list):
    client = MongoClient(uri)
    db = client[db_name]

    # Campos a excluir en la consulta
    exclusion = {"_id": 0, "image": 0, "description": 0}
    productos_activos = db[coleccion_origen].find({"status": "active"}, exclusion)
    
    for producto in productos_activos:
        # Obtiene el SKU del producto
        sku = producto.get("sku")
        precio_compra_dia = precio_familia_compra(uri, db_name, sku, operation_date)

        # Encuentra la equivalencia
        equivalence_match = next(
            (
                item for item in equivalence_data
                if str(item.get('ARTICULO')) == str(producto.get("sipsa_id")) 
                and pd.to_datetime(item.get('FECHA'), errors='coerce') == pd.to_datetime(operation_date)
            ),
            None
        )
        # Calcula valores mínimos, máximos y promedio
        minimoKg = float(equivalence_match["MINIMO"])* float(producto["step_unit_sipsa"])  if equivalence_match else 0
        maximoKg = float(equivalence_match["MAXIMO"])* float(producto["step_unit_sipsa"])  if equivalence_match else 0
        promedioKg = float(equivalence_match["PROMEDIO"])* float(producto["step_unit_sipsa"])  if equivalence_match else 0

        # Define el price_purchase según la regla dada
        if precio_compra_dia != 0:
            price_purchase = precio_compra_dia  * float(producto["step_unit"])
        elif promedioKg != 0:
            price_purchase = maximoKg
        else:
            price_purchase = producto.get("price_purchase", 0)


        price_purchase = price_purchase * float(producto.get("factor_volumen", 1))
        margen = producto.get("margen", 0)
        price_sale = price_purchase * (1 + margen)

        # Actualiza el producto con la información nueva
        producto.update({
            "operation_date": operation_date,
            "last_price_purchased": round(precio_compra_dia) if precio_compra_dia else 0,
            "minimoKg": round(minimoKg),
            "maximoKg": round(maximoKg),
            "promedioKg": round(promedioKg),
            "price_purchase": round(price_purchase),
            "price_sale": round(price_sale),
            "last_price_purchase": round(producto.get("price_purchase", 0)),
            "last_price_sale": round(producto.get("price_sale", 0))
        })


        # Inserta el producto actualizado en la colección de destino
        db[coleccion_destino].insert_one(producto)

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

uri = 'mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp'
db_name = "frescapp"
coleccion_origen = "products"
coleccion_destino = "products_history"
fields = ['ARTICULO', 'PROMEDIO', 'MINIMO', 'MAXIMO', 'FECHA', 'FUENTE']
operation_date ='2024-11-08'
filepath = os.path.join(os.path.dirname(__file__), f"sipsaexporta_{operation_date}.xls")


obtenerSipsa(operation_date,filepath)
data = extractDataFromExcel(filepath, operation_date)
# copiar_productos_activos_y_actualizar(uri, db_name, coleccion_origen, coleccion_destino, operation_date, data)
# actualizar_precios_en_products(uri, db_name, coleccion_destino, operation_date)
# if os.path.exists(filepath):
#     os.remove(filepath)

