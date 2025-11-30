import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------
# CONFIGURACIÓN DE CONEXIONES
# -------------------------------------
PROD_URI = os.getenv("MONGO_URI_PROD")
DEV_URI = os.getenv("MONGO_URI")

if not PROD_URI or not DEV_URI:
    raise Exception("❌ Variables MONGO_URI_PROD o MONGO_URI no están definidas.")

prod_client = MongoClient(PROD_URI)
dev_client = MongoClient(DEV_URI)

prod_db = prod_client[PROD_URI.split('/')[-1].split('?')[0] or "frescapp"]
dev_db = dev_client[DEV_URI.split('/')[-1].split('?')[0] or "admon28"]

# -------------------------------------
# COLECCIONES A COPIAR
# -------------------------------------
TARGET_COLLECTIONS = [
    "products",
    "orders",
    "customers",
    "users",
    "inventory",
    "purchases",
    "costs"
]

print("🚀 Iniciando copia de colecciones:")
print("🔹 Producción →", PROD_URI)
print("🔹 Desarrollo →", DEV_URI)
print("---------------------------------------------------")

# -------------------------------------
# COPIAR COLECCIÓN POR COLECCIÓN
# -------------------------------------
for col_name in TARGET_COLLECTIONS:
    print(f"\n📦 Procesando colección: {col_name}")

    prod_col = prod_db[col_name]
    dev_col = dev_db[col_name]

    prod_count = prod_col.count_documents({})
    print(f"   - Documentos en PROD: {prod_count}")

    # Limpiar colección destino
    dev_col.delete_many({})
    print("   - DEV limpiado.")

    if prod_count == 0:
        print("   - ❗ Colección en blanco en PROD, se omite.")
        continue

    # Copiar documentos
    docs = list(prod_col.find({}))
    if docs:
        # Quitar el _id para evitar duplicados
        for d in docs:
            d.pop("_id", None)

        dev_col.insert_many(docs)
        print(f"   - {len(docs)} documentos copiados a DEV.")

    dev_count = dev_col.count_documents({})
    print(f"   - Total en DEV: {dev_count}")

print("\n🎉 Proceso completado con éxito.")
