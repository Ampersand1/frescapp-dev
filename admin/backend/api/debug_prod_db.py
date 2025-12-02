import os
from bson import ObjectId
from flask import Blueprint
from pymongo import MongoClient

debug_prod_api = Blueprint("debug_prod_api", __name__)
def serialize_mongo(doc):
    """
    Convierte todos los ObjectId dentro de un dict a str.
    Funciona recursivamente en listas y subdicts.
    """
    if isinstance(doc, list):
        return [serialize_mongo(d) for d in doc]
    elif isinstance(doc, dict):
        return {k: serialize_mongo(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

@debug_prod_api.route("/api/debug/prod_admins")
def debug_prod_admins():
    try:
        prod_uri = os.getenv("MONGO_URI_PROD")
        if not prod_uri:
            return {"error": "MONGO_URI_PROD no está configurado"}, 500

        client = MongoClient(prod_uri)
        db_name = prod_uri.split('/')[-1].split('?')[0] or "frescapp"
        db = client[db_name]

        users_collections = ['users', 'customers']
        admins_list = []

        for collection_name in users_collections:
            col = db[collection_name]
            admins = list(col.find(
                {"category": {"$in": ["Restaurante Ejecutivo", "Admin", "Administrador"]}},
                {"_id": 1, "name": 1, "user": 1, "email": 1, "category": 1}
            ))
            admins_list.extend(serialize_mongo(admins))

        return {
            "status": "ok",
            "possible_admins": admins_list,
            "db_name": db_name
        }

    except Exception as e:
        return {"error": str(e)}, 500
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