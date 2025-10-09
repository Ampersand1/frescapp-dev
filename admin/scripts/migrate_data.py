"""
Script seguro para migrar datos entre la base de producción y la de pruebas (admon28)
Autor: ChatGPT x Esposa Mía 💕
"""

from pymongo import MongoClient, errors
import os
from pprint import pprint

# === CONFIGURACIÓN ===
PROD_URI = os.getenv("MONGO_URI_PROD", "mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp")
DEV_URI = os.getenv("MONGO_URI", "mongodb+srv://admon28vrv:vrv1928CLUSpas@cluster-1.j6mqxz0.mongodb.net/admon28?retryWrites=true&w=majority")

PROD_DB_NAME = "frescapp"
DEV_DB_NAME = "admon28"

# === COLECCIONES A MIGRAR ===
# ✨ Puedes agregar o quitar nombres de colecciones libremente
COLECCIONES_A_MIGRAR = [
    "routes",       # rutas de entrega
    # "clients",    # clientes (si quieres)
    # "orders",     # pedidos
    # "costs",      # costos
]

# === CONEXIÓN ===
try:
    client_prod = MongoClient(PROD_URI)
    db_prod = client_prod[PROD_DB_NAME]

    client_dev = MongoClient(DEV_URI)
    db_dev = client_dev[DEV_DB_NAME]

    print("✅ Conectado correctamente a ambas bases de datos:")
    print(f"   - Producción: {PROD_DB_NAME}")
    print(f"   - Pruebas: {DEV_DB_NAME}")

except errors.ConnectionFailure as e:
    print("❌ Error al conectar con MongoDB:", e)
    exit(1)

# === VERIFICAR PERMISOS DE ESCRITURA ===
try:
    test_result = db_dev["_auth_test"].insert_one({"ok": True})
    db_dev["_auth_test"].delete_one({"_id": test_result.inserted_id})
    print("✅ Usuario con permisos de escritura en la base de pruebas.")
except errors.OperationFailure:
    print("⚠️ No tienes permisos de escritura en la base de pruebas.")
    print("   Verifica el rol del usuario 'admon28vrv' en MongoDB Atlas (debe ser 'readWrite').")
    exit(1)

# === MIGRACIÓN ===
for nombre in COLECCIONES_A_MIGRAR:
    print(f"\n➡️ Migrando colección: {nombre}")

    col_prod = db_prod[nombre]
    col_dev = db_dev[nombre]

    documentos = list(col_prod.find())
    print(f"   Encontrados {len(documentos)} documentos en producción.")

    if not documentos:
        continue

    migrados = 0
    for doc in documentos:
        # Evita duplicados en base de pruebas
        if col_dev.find_one({"_id": doc["_id"]}):
            continue
        try:
            col_dev.insert_one(doc)
            migrados += 1
        except errors.DuplicateKeyError:
            continue

    print(f"   ✅ {migrados} documentos nuevos copiados a {DEV_DB_NAME}.{nombre}")

print("\n🎉 Migración completada exitosamente.")
