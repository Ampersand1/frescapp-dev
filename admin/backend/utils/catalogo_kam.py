from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
collection = db['customers']

# Variable con el JSON base
catalogo_match = [
 {
   "equivalente": "ACELGA ",
   "step_unit": 2,
   "sku": "BOG-CAT004-00007"
 },
 {
   "equivalente": "AGUACATE  EXTRA SELECTO",
   "step_unit": 1,
   "sku": "BOG-CAT002-00021"
 },
 {
   "equivalente": "AGUACATE  EXTRA SELECTO",
   "step_unit": 1,
   "sku": "BOG-CAT002-00021"
 },
 {
   "equivalente": "AHUYAMA AMARILLA",
   "step_unit": 0.3,
   "sku": "BOG-CAT001-00010"
 },
 {
   "equivalente": "AHUYAMA ZAPAYO",
   "step_unit": 1,
   "sku": "BOG-CAT001-00025"
 },
 {
   "equivalente": "AJI PROCESADO ",
   "step_unit": 0,
   "sku": ""
 },
 {
   "equivalente": "AJO IMPORTADO SIN PELAR",
   "step_unit": 1,
   "sku": "BOG-CAT001-00006"
 },
 {
   "equivalente": "AJO PELADO IMPORTADO",
   "step_unit": 0,
   "sku": ""
 },
 {
   "equivalente": "ALBAHACA",
   "step_unit": 2,
   "sku": "BOG-CAT004-00027"
 },
 {
   "equivalente": "APIO ",
   "step_unit": 1,
   "sku": " BOG-CAT005-00099\t"
 },
 {
   "equivalente": "ARRACACHA CERO",
   "step_unit": 1,
   "sku": "BOG-CAT003-00003"
 },
 {
   "equivalente": "ARVEJA DESGRANADA",
   "step_unit": 1,
   "sku": "BOG-CAT001-00059"
 },
 {
   "equivalente": "ARVEJA DESGRANADA PRIMERA",
   "step_unit": 1,
   "sku": "BOG-CAT001-00059"
 },
 {
   "equivalente": "BANANO CRIOLLO ",
   "step_unit": 1,
   "sku": "BOG-CAT002-00047"
 },
 {
   "equivalente": "BANANO URABA",
   "step_unit": 1,
   "sku": "BOG-CAT002-00047"
 },
 {
   "equivalente": "BERENJENA",
   "step_unit": 1,
   "sku": "BOG-CAT001-00016"
 },
 {
   "equivalente": "BROCOLI",
   "step_unit": 1,
   "sku": " BOG-CAT005-00103\t"
 },
 {
   "equivalente": "CALABACÍN ",
   "step_unit": 0.5,
   "sku": "BOG-CAT001-00024"
 },
 {
   "equivalente": "CALABAZA ",
   "step_unit": 1,
   "sku": " BOG-CAT004-00023\t"
 },
 {
   "equivalente": "CEBOLLA CABEZONA BLANCA  CERO LIMPIA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00019"
 },
 {
   "equivalente": "CEBOLLA CABEZONA ROJA PELADA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00057"
 },
 {
   "equivalente": "CEBOLLA LARGA (JUNCA)",
   "step_unit": 1,
   "sku": " BOG-CAT001-00008"
 },
 {
   "equivalente": "CEBOLLA PUERRO",
   "step_unit": 1,
   "sku": " BOG-CAT001-00092\t"
 },
 {
   "equivalente": "CEBOLLIN",
   "step_unit": 4,
   "sku": " BOG-CAT001-00087\t"
 },
 {
   "equivalente": "CHAMPIÑONES ",
   "step_unit": 2,
   "sku": " BOG-CAT001-00040"
 },
 {
   "equivalente": "CILANTRO",
   "step_unit": 1,
   "sku": " BOG-CAT004-00001"
 },
 {
   "equivalente": "COCO GRANDE",
   "step_unit": 1,
   "sku": " BOG-CAT002-00039"
 },
 {
   "equivalente": "COLICERO",
   "step_unit": 1,
   "sku": "BOG-CAT001-00023"
 },
 {
   "equivalente": "COLIFLOR ",
   "step_unit": 1,
   "sku": "BOG-CAT004-00014"
 },
 {
   "equivalente": "CURUBA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00090\t"
 },
 {
   "equivalente": "DURAZNO",
   "step_unit": 1,
   "sku": " BOG-CAT002-00023"
 },
 {
   "equivalente": "ESPARRAGOS",
   "step_unit": 2,
   "sku": " BOG-CAT001-00073"
 },
 {
   "equivalente": "ESPINACA",
   "step_unit": 1,
   "sku": " BOG-CAT005-00100\t"
 },
 {
   "equivalente": "FEIJOA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00083\t"
 },
 {
   "equivalente": "FRESA EXTRA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00069\t"
 },
 {
   "equivalente": "FRESA JUGO",
   "step_unit": 1,
   "sku": " BOG-CAT002-00011"
 },
 {
   "equivalente": "FRIJOL VERDE DESGRANADO",
   "step_unit": 1,
   "sku": " BOG-CAT001-00062"
 },
 {
   "equivalente": "GRANADILLA 1",
   "step_unit": 1,
   "sku": " BOG-CAT002-00088\t"
 },
 {
   "equivalente": "GUANABANA",
   "step_unit": 0.5,
   "sku": " BOG-CAT002-00033"
 },
 {
   "equivalente": "GUASCAS",
   "step_unit": 1,
   "sku": " BOG-CAT001-00042\t"
 },
 {
   "equivalente": "GUATILA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00074\t"
 },
 {
   "equivalente": "GUAYABA COMUN",
   "step_unit": 1,
   "sku": " BOG-CAT002-00007\t"
 },
 {
   "equivalente": "GUAYABA PERA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00007\t"
 },
 {
   "equivalente": "HABA VERDE DESGRANADA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00072\t"
 },
 {
   "equivalente": "HABICHUELA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00009\t"
 },
 {
   "equivalente": "HIERBABUENA",
   "step_unit": 1,
   "sku": " BOG-CAT005-00101\t"
 },
 {
   "equivalente": "JENGIBRE",
   "step_unit": 1,
   "sku": " BOG-CAT004-00032\t"
 },
 {
   "equivalente": "KIWI",
   "step_unit": 1,
   "sku": " BOG-CAT002-00065\t"
 },
 {
   "equivalente": "LAUREL Y TOMILLO ",
   "step_unit": 1,
   "sku": " BOG-CAT004-00024\t"
 },
 {
   "equivalente": "LECHUGA BATAVIA",
   "step_unit": 1,
   "sku": " BOG-CAT004-00003\t"
 },
 {
   "equivalente": "LECHUGA CRESPA MORADA HIDRO",
   "step_unit": 1,
   "sku": " BOG-CAT004-00010\t"
 },
 {
   "equivalente": "LECHUGA CRESPA VERDE HIDRO",
   "step_unit": 1,
   "sku": " BOG-CAT004-00002\t"
 },
 {
   "equivalente": "LIMON TAHITI EXTRA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00056\t"
 },
 {
   "equivalente": "LULO ",
   "step_unit": 1,
   "sku": " BOG-CAT002-00009\t"
 },
 {
   "equivalente": "MANDARINA X 100 GR",
   "step_unit": 1,
   "sku": " BOG-CAT002-00050\t"
 },
 {
   "equivalente": "MANGO DE AZUCAR",
   "step_unit": 1,
   "sku": " BOG-CAT002-00054\t"
 },
 {
   "equivalente": "MANGO FACHIR",
   "step_unit": 1,
   "sku": " BOG-CAT002-00006\t"
 },
 {
   "equivalente": "MANGO TOMMY BICHE",
   "step_unit": 1,
   "sku": " BOG-CAT002-00006\t"
 },
 {
   "equivalente": "MANGO TOMY MADURO",
   "step_unit": 1,
   "sku": " BOG-CAT002-00006\t"
 },
 {
   "equivalente": "MANZANA ROJA CHILENA 125",
   "step_unit": 1,
   "sku": " BOG-CAT002-00073\t"
 },
 {
   "equivalente": "MANZANA ROYAL",
   "step_unit": 1,
   "sku": " BOG-CAT002-00073\t"
 },
 {
   "equivalente": "MANZANA VERDE CHILENA 125",
   "step_unit": 1,
   "sku": " BOG-CAT002-00087\t"
 },
 {
   "equivalente": "MARACUYA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00005\t"
 },
 {
   "equivalente": "MAZORCA DESGRANADA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00021\t"
 },
 {
   "equivalente": "MAZORCA TUSA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00012\t"
 },
 {
   "equivalente": "MELON",
   "step_unit": 1,
   "sku": " BOG-CAT002-00048\t"
 },
 {
   "equivalente": "MORA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00036\t"
 },
 {
   "equivalente": "MUTE",
   "step_unit": 1,
   "sku": ""
 },
 {
   "equivalente": "NARANJA TANGELO",
   "step_unit": 1,
   "sku": ""
 },
 {
   "equivalente": "NARANJA VALENCIA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00003\t"
 },
 {
   "equivalente": "PAPA CRIOLLA CERO",
   "step_unit": 1,
   "sku": " BOG-CAT003-00034\t"
 },
 {
   "equivalente": "PAPA CRIOLLA PRIMERA",
   "step_unit": 1,
   "sku": " BOG-CAT003-00034\t"
 },
 {
   "equivalente": "PAPA PASTUSA PRIMERA LAVADA",
   "step_unit": 1,
   "sku": " BOG-CAT003-00033\t"
 },
 {
   "equivalente": "PAPA R12 GRUESA",
   "step_unit": 1,
   "sku": " BOG-CAT003-00031\t"
 },
 {
   "equivalente": "PAPA R12 PAREJA",
   "step_unit": 1,
   "sku": " BOG-CAT003-00035\t"
 },
 {
   "equivalente": "PAPA SABANERA ",
   "step_unit": 1,
   "sku": " BOG-CAT003-00006\t"
 },
 {
   "equivalente": "PAPAYA MARADOL",
   "step_unit": 1,
   "sku": " BOG-CAT002-00086\t"
 },
 {
   "equivalente": "PAPAYUELA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00059\t"
 },
 {
   "equivalente": "PATILLA",
   "step_unit": 0.3,
   "sku": " BOG-CAT002-00014\t"
 },
 {
   "equivalente": "PEPINO COHOMBRO",
   "step_unit": 1,
   "sku": " BOG-CAT001-00007\t"
 },
 {
   "equivalente": "PEPINO COMÚN",
   "step_unit": 1,
   "sku": " BOG-CAT001-00018\t"
 },
 {
   "equivalente": "PERA IMPORTADA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00075\t"
 },
 {
   "equivalente": "PEREJIL CRESPO",
   "step_unit": 1,
   "sku": " BOG-CAT004-00006\t"
 },
 {
   "equivalente": "PIMENTON  VERDE ESTANDAR",
   "step_unit": 1,
   "sku": " BOG-CAT001-00064\t"
 },
 {
   "equivalente": "PIMENTÓN AMARILLO",
   "step_unit": 1,
   "sku": " BOG-CAT001-00088\t"
 },
 {
   "equivalente": "PIMENTON ROJO ESTÁNDAR",
   "step_unit": 1,
   "sku": " BOG-CAT001-00005\t"
 },
 {
   "equivalente": "PIÑA GOLD",
   "step_unit": 1,
   "sku": " BOG-CAT002-00002\t"
 },
 {
   "equivalente": "PIÑA PEROLERA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00060\t"
 },
 {
   "equivalente": "PITAHAYA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00068\t"
 },
 {
   "equivalente": "PLÁTANO MADURO LLANERO",
   "step_unit": 1,
   "sku": " BOG-CAT002-00034\t"
 },
 {
   "equivalente": "PLÁTANO VERDE  LLANERO",
   "step_unit": 1,
   "sku": " BOG-CAT002-00004\t"
 },
 {
   "equivalente": "RABANO",
   "step_unit": 1,
   "sku": " BOG-CAT001-00054\t"
 },
 {
   "equivalente": "RAIZ CHINA",
   "step_unit": 1,
   "sku": " BOG-CAT004-00028\t"
 },
 {
   "equivalente": "REMOLACHA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00020\t"
 },
 {
   "equivalente": "REPOLLO BLANCO",
   "step_unit": 1,
   "sku": " BOG-CAT005-00096\t"
 },
 {
   "equivalente": "REPOLLO MORADO",
   "step_unit": 1,
   "sku": " BOG-CAT005-00102\t"
 },
 {
   "equivalente": "TOMATE CHERRY",
   "step_unit": 1,
   "sku": " BOG-CAT001-00011\t"
 },
 {
   "equivalente": "TOMATE CHONTO PRIMERA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00003\t"
 },
 {
   "equivalente": "TOMATE CHONTO SELECTO",
   "step_unit": 1,
   "sku": " BOG-CAT001-00003\t"
 },
 {
   "equivalente": "TOMATE DE ARBOL",
   "step_unit": 1,
   "sku": " BOG-CAT002-00046\t"
 },
 {
   "equivalente": "TOMATE LARGA VIDA EXTRA PINTON",
   "step_unit": 1,
   "sku": " BOG-CAT001-00022\t"
 },
 {
   "equivalente": "UVA ISABELLA",
   "step_unit": 1,
   "sku": " BOG-CAT002-00079\t"
 },
 {
   "equivalente": "YUCA LAVADA",
   "step_unit": 1,
   "sku": " BOG-CAT003-00036\t"
 },
 {
   "equivalente": "ZANAHORIA",
   "step_unit": 1,
   "sku": " BOG-CAT001-00069\t"
 },
 {
   "equivalente": "ZUQUINI AMARILLO",
   "step_unit": 1,
   "sku": " BOG-CAT001-00015\t"
 },
 {
   "equivalente": "ZUQUINI VERDE",
   "step_unit": 1,
   "sku": " BOG-CAT001-00014\t"
 }
]

# Convertir JSON a array (si es necesario)
#catalogo_match = list(json_data.values())

# Actualizar el documento con email "xxx"
result = collection.update_one(
    {"email": "facturacion.sextosas@gmail.com"},
    {"$set": {"match_catalogo": catalogo_match}}
)

# Confirmar resultado
if result.modified_count:
    print("Documento actualizado correctamente.")
else:
    print("No se encontró el documento o ya estaba actualizado.")
