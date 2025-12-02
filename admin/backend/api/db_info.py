import os
from flask import Blueprint
from ..db import get_db

debug_db_api = Blueprint("debug_db_api", __name__)

@debug_db_api.route('/db_info', methods=['GET'])
def debug_db_info():
    try:
        db = get_db()

        env = os.getenv("FLASK_ENV", "development")
        uri = os.getenv("MONGO_URI_PROD") if env == "production" else os.getenv("MONGO_URI")

        # Sanitizar la URI (para evitar mostrar usuario/contraseña)
        sanitized_uri = uri
        if "@" in uri:
            sanitized_uri = uri.split("://")[0] + "://<hidden>@" + uri.split("@")[1]

        collections = db.list_collection_names()

        # Conteo de documentos por colección
        counts = {}
        for col in collections:
            try:
                counts[col] = db[col].count_documents({})
            except:
                counts[col] = "error"

        return {
            "status": "ok",
            "environment": env,
            "db_uri_used": sanitized_uri,
            "db_name": db.name,
            "collections": collections,
            "counts": counts,
        }, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
