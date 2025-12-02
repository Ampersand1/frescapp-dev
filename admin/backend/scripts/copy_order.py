import os
from pymongo import MongoClient
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def extract_db_name(uri: str, default_name: str):
    """
    Extrae el nombre real de la base de datos desde un URI de MongoDB.
    Si no hay nombre explícito, usa un nombre por defecto.
    """
    parsed = urlparse(uri)
    db_name = parsed.path.lstrip('/')  # elimina "/"

    # Si está vacío, usamos el nombre por defecto
    if not db_name or db_name == "":
        print(f"⚠️  No se encontró nombre de BD en el URI. Usando BD por defecto: {default_name}")
        return default_name

    # Si tiene parámetros, quitar ?xxx
    return db_name.split("?")[0]


# -------------------------------------
# CONEXIONES
# -------------------------------------
PROD_URI = os.getenv("MONGO_URI_PROD")
DEV_URI = os.getenv("MONGO_URI")

if not PROD_URI or not DEV_URI:
    raise Exception("❌ Variables MONGO_URI_PROD o MONGO_URI no están definidas.")

prod_client = MongoClient(PROD_URI)
dev_client = MongoClient(DEV_URI)

prod_db_name = extract_db_name(PROD_URI, "frescapp")
dev_db_name = extract_db_name(DEV_URI, "admon28")  # BD por defecto

prod_db = prod_client[prod_db_name]
dev_db = dev_client[dev_db_name]

print(f"📌 Base de datos PROD: {prod_db_name}")
print(f"📌 Base de datos DEV:  {dev_db_name}")

# -------------------------------------
# COLECCIONES A COPIAR
# -------------------------------------
TARGET_COLLECTIONS = [
    "orderConfig"
]

print("\n🚀 Iniciando copia de colecciones:")
print("---------------------------------------------------")

for col_name in TARGET_COLLECTIONS:
    print(f"\n📦 Procesando colección: {col_name}")

    prod_col = prod_db[col_name]
    dev_col = dev_db[col_name]

    prod_count = prod_col.count_documents({})
    print(f"   - Documentos en PROD: {prod_count}")

    dev_col.delete_many({})  # Limpiar destino
    print("   - DEV limpiado.")

    if prod_count == 0:
        print("   ❗ PROD está vacío, nada que copiar.")
        continue

    docs = list(prod_col.find({}))
    for d in docs:
        d.pop("_id", None)

    dev_col.insert_many(docs)
    print(f"   - {len(docs)} documentos copiados.")

print("\n🎉 Proceso completado con éxito.")
