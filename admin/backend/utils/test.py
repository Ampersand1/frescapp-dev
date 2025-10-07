import requests, os
url = "https://apps.dane.gov.co/pentaho/plugin/cda/api/doQuery"
timeout = 120 
operation_date ='2025-07-03'
path_destino = os.path.join(os.path.dirname(__file__), f"sipsaexporta_{operation_date}.xls")

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
