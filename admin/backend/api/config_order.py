from flask import Blueprint, jsonify, current_app

configOrder_api = Blueprint('config_order', __name__)

# --- Función para obtener la base de datos correctamente dentro del contexto ---
def get_db():
    from ..db import get_db
    return get_db()

@configOrder_api.route('/configOrder', methods=['GET'])
def config_order():
    """
    Obtiene la configuración de la orden almacenada en la colección 'orderConfig'.
    """
    try:
        db = get_db()
        config_collection = db['orderConfig']

        # Buscar un documento (sin el campo _id)
        config_data = config_collection.find_one({}, {'_id': 0})

        if config_data:
            return jsonify(config_data), 200
        else:
            return jsonify({'error': 'Configuración de orden no encontrada'}), 404

    except Exception as e:
        current_app.logger.error(f"Error al obtener configuración de orden: {e}")
        return jsonify({'error': f'Error al obtener la configuración de orden: {str(e)}'}), 500
