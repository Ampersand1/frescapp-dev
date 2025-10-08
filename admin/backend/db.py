import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask import current_app

# Cargar variables del archivo .env
load_dotenv()

# Variable global para conexión
mongo = None


def init_db(app):
    """
    Inicializa la conexión a MongoDB y la asocia con la app Flask.
    """
    global mongo

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("❌ MONGO_URI no está definida en el archivo .env")

    app.config["MONGO_URI"] = mongo_uri
    mongo = PyMongo(app)
    return mongo


def get_db():
    """
    Retorna una instancia de base de datos activa, ya inicializada con init_db(app).
    Si se llama fuera del contexto de Flask, lanza error.
    """
    global mongo
    if mongo is None:
        try:
            # Si la app Flask está corriendo, usar su contexto actual
            mongo = PyMongo(current_app)
        except Exception:
            raise RuntimeError("❌ No se ha inicializado la conexión a la base de datos. Llama a init_db(app) antes de usar get_db().")

    return mongo.db
