from flask import Flask, send_file, make_response, request, Response, send_from_directory
from flask_cors import CORS
import os
from api.order_management import order_api
from api.product_management import product_api
from api.customer_management import customer_api
from api.user_management import user_api
from api.config_order import configOrder_api
from api.reports_management import report_api
from api.discount_management import discount_api
from api.alegra_management import alegra_api
from api.woo_management import woo_api
from api.purchase_management import purchase_api
from api.action_management import action_api
from api.supplier_management import supplier_api
from api.route_management import route_api
from api.product_history_management import product_history_api
from api.ue_management import ue_api
from api.cost_management import cost_api
from api.inventory_management import inventory_api
from api.analytics_management import analytics_api
from api.cierre_management import cierres_api
from api.strikes_management import strike_api
if __name__ == '__main__':
    app = Flask(__name__)
    # Configura la aplicación utilizando el archivo config.py
    app.config.from_pyfile('config.py')

    # Token secreto para autenticación

    # Registra los blueprints de los diferentes módulos de la aplicación
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


    @app.route('/api/shared/<path:filename>')
    def serve_static(filename):
        root_dir = os.path.dirname(os.getcwd())
        file_path = os.path.join(root_dir, 'backend', 'shared', 'products', filename)
        
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(root_dir, 'backend', 'shared', 'products'), filename)
        else:
            # Si el archivo no existe, envía sin_foto.png
            return send_from_directory(os.path.join(root_dir, 'backend', 'shared'), 'sin_foto.png')


    # Configurar CORS para permitir solicitudes desde cualquier origen
    
    CORS(app, resources={"/*": {"origins": "*"}})
    context = ('/etc/ssl/certs/app_buyfrescapp_com.crt', '/etc/ssl/certs/app_buyfrescapp_com.key')

    #app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', port=5000, ssl_context=context)

