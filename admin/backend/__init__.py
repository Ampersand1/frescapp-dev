from flask import Flask
from .api.customer_management import customer_api
from .api.product_management import product_api
from .api.order_management import order_api
from .models.database import db

# Crea la instancia de la aplicación Flask
app = Flask(__name__)

# Configura la aplicación utilizando el archivo config.py
app.config.from_pyfile('config.py')

# Registra los blueprints de los diferentes módulos de la aplicación
app.register_blueprint(customer_api, url_prefix='/api/customer')
app.register_blueprint(product_api, url_prefix='/api/product')
app.register_blueprint(order_api, url_prefix='/api/order')

# Inicializa la base de datos
db.init_app(app)
