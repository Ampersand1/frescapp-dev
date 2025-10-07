from flask import Blueprint, jsonify
from pymongo import MongoClient

configOrder_api = Blueprint('config_order', __name__)

# Conexión a la base de datos MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
config_collection = db['orderConfig']

@configOrder_api.route('/configOrder', methods=['GET'])
def configOrder():
    try:
        # Obtener la configuración de la orden desde la base de datos
        config_data = config_collection.find_one({},{'_id': 0})
        if config_data:
            # Convertir el objeto a un diccionario
            config_dict = dict(config_data)
            # Devolver los datos de configuración como respuesta JSON
            return jsonify(config_dict), 200
        else:
            # Si no se encuentra ninguna configuración, devolver un mensaje de error
            return jsonify({'error': 'Configuración de orden no encontrada'}), 404
    except Exception as e:
        # Capturar cualquier excepción y devolver un mensaje de error genérico
        return jsonify({'error': 'Error al obtener la configuración de orden: {}'.format(str(e))}), 500
