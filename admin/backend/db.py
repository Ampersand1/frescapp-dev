from flask_pymongo import PyMongo

mongo = None

def init_db(app):
    """Inicializa la conexión a MongoDB con la app Flask."""
    global mongo
    mongo = PyMongo(app)
    return mongo

def get_db():
    """Obtiene la base de datos MongoDB ya inicializada."""
    global mongo
    if mongo:
        return mongo.db
    else:
        raise Exception("Database not initialized. Call init_db(app) first.")
