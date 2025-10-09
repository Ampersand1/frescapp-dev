import os
from pymongo import MongoClient

client = None
db = None

def init_db(app=None):
    global client, db

    env = os.getenv("FLASK_ENV", "development")

    # Usa MONGO_URI_PROD si estás en producción, si no, usa MONGO_URI
    mongo_uri = os.getenv("MONGO_URI_PROD") if env == "production" else os.getenv("MONGO_URI")

    if not mongo_uri:
        raise Exception("❌ No se encontró la URI de MongoDB en las variables de entorno.")

    client = MongoClient(mongo_uri)
    db_name = mongo_uri.split('/')[-1].split('?')[0] or 'admon28'
    db = client[db_name]

    print(f"✅ Conectado a MongoDB ({env}): {db_name}")
    return db

def get_db():
    global db
    if db is None:
        print("⚠️ Base de datos no inicializada. Inicializando automáticamente...")
        return init_db()
    return db
