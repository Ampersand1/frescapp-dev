import os
from flask import Blueprint
from pymongo import MongoClient

debug_prod_api = Blueprint("debug_prod_api", __name__)

@debug_prod_api.route("/api/debug/prod_db")
def debug_prod_db():
    try:
        prod_uri = os.getenv("MONGO_URI_PROD")
        if not prod_uri:
            return {"error": "MONGO_URI_PROD no está configurado"}, 500

        client = MongoClient(prod_uri)

        # Obtener nombre real de la base de datos desde la URI
        db_name = prod_uri.split('/')[-1].split('?')[0] or "frescapp"
        db = client[db_name]

        # Sanitizar URI para no mostrar contraseñas
        sanitized_uri = prod_uri.split("://")[0] + "://<hidden>@" + prod_uri.split("@")[1]

        collections = db.list_collection_names()

        counts = {}
        for col in collections:
            try:
                counts[col] = db[col].count_documents({})
            except:
                counts[col] = "error"

        return {
            "status": "ok",
            "db_name": db_name,
            "prod_db_uri": sanitized_uri,
            "collections": collections,
            "counts": counts
        }

    except Exception as e:
        return {"error": str(e)}, 500
