from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
from .db import init_db
from flask_pymongo import PyMongo
# ---------------------------
# Cargar variables de entorno
# ---------------------------
load_dotenv()

def init_db(app):
    uri = os.getenv("MONGO_URI")  # por defecto, desarrollo
    if not uri:
        raise ValueError("MONGO_URI no está configurada en el archivo .env")
    app.config["MONGO_URI"] = uri
    mongo = PyMongo(app)
    return mongo
# ---------------------------
# Inicializar aplicación Flask
# ---------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_por_defecto")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
# ---------------------------
# Inicializar conexión con MongoDB
# ---------------------------

mongo = init_db(app)
db = mongo.db  

# ---------------------------
# Importar y registrar Blueprints
# ---------------------------
from .api.order_management import order_api
from .api.product_management import product_api
from .api.customer_management import customer_api
from .api.user_management import user_api
from .api.config_order import configOrder_api
from .api.reports_management import report_api
from .api.discount_management import discount_api
from .api.alegra_management import alegra_api
from .api.woo_management import woo_api
from .api.purchase_management import purchase_api
from .api.action_management import action_api
from .api.supplier_management import supplier_api
from .api.route_management import route_api
from .api.product_history_management import product_history_api
from .api.ue_management import ue_api
from .api.cost_management import cost_api
from .api.inventory_management import inventory_api
from .api.analytics_management import analytics_api
from .api.cierre_management import cierres_api
from .api.strikes_management import strike_api

# Registro de rutas
app.register_blueprint(order_api, url_prefix='/api/order')
app.register_blueprint(product_api, url_prefix='/api/product')
app.register_blueprint(product_history_api, url_prefix='/api/products_history')
app.register_blueprint(customer_api, url_prefix='/api/customer')
app.register_blueprint(user_api, url_prefix='/api/user')
app.register_blueprint(configOrder_api, url_prefix='/api/config')
app.register_blueprint(report_api, url_prefix='/api/reports')
app.register_blueprint(discount_api, url_prefix='/api/discount')
app.register_blueprint(alegra_api, url_prefix='/api/alegra')
app.register_blueprint(woo_api, url_prefix='/api/woo')
app.register_blueprint(purchase_api, url_prefix='/api/purchase')
app.register_blueprint(action_api, url_prefix='/api/action')
app.register_blueprint(supplier_api, url_prefix='/api/supplier')
app.register_blueprint(route_api, url_prefix='/api/route')
app.register_blueprint(ue_api, url_prefix='/api/ue')
app.register_blueprint(cost_api, url_prefix='/api/cost')
app.register_blueprint(inventory_api, url_prefix='/api/inventory')
app.register_blueprint(analytics_api, url_prefix='/api/analytics')
app.register_blueprint(cierres_api, url_prefix='/api/cierres')
app.register_blueprint(strike_api, url_prefix='/api/strikes')

# ---------------------------
# Ruta raíz (para ver si el backend está vivo)
# ---------------------------
@app.route('/')
def home():
    return {
        "status": "ok",
        "message": "Backend de Frescapp funcionando correctamente UwU"
    }
@app.route("/api/test_db")
def test_db():
    try:
        mongo_stats = db.command("dbstats")
        return {"status": "ok", "db_name": mongo_stats["db"], "collections": mongo_stats["collections"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

# ---------------------------
# Servir archivos estáticos (imágenes compartidas)
# ---------------------------
@app.route('/api/shared/<path:filename>')
def serve_static(filename):
    """
    Sirve imágenes de productos desde 'backend/shared/products'.
    Si no existe, retorna 'sin_foto.png'.
    """
    root_dir = os.path.dirname(os.getcwd())
    products_dir = os.path.join(root_dir, 'backend', 'shared', 'products')
    file_path = os.path.join(products_dir, filename)

    if os.path.exists(file_path):
        return send_from_directory(products_dir, filename)
    else:
        return send_from_directory(os.path.join(root_dir, 'backend', 'shared'), 'sin_foto.png')

# ---------------------------
# Habilitar CORS
# ---------------------------
CORS(app, resources={r"/*": {"origins": "*"}})

# ---------------------------
# Ejecutar servidor
# ---------------------------
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    print(f"🚀 Servidor iniciado en: http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
