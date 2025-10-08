from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from db import get_db

# Inicializa el blueprint
action_api = Blueprint('action', __name__)

# Conexión centralizada (usando db.py)
db = get_db()
actions_collection = db['actions']
potential_customers = db['potential_customers']
counters_collection = db['counters']


# Crear una nueva acción
@action_api.route('/action', methods=['POST'])
def create_action():
    data = request.json
    if not data:
        return jsonify({"status": "failure", "message": "No data provided"}), 400
    
    actionNumber = db['counters'].find_one_and_update(
        {"_id": "action_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )["sequence_value"]

    new_action = {
        "actionNumber": str(actionNumber),
        "dateAction": data.get("dateAction"),
        "dateSolution": data.get("dateSolution"),
        "type": data.get("type"),
        "customer": data.get("customer"),
        "orderNumber": data.get("orderNumber"),
        "manager": data.get("manager"),
        "status": data.get("status", "Creada"),
        "actionComment": data.get("actionComment"),
        "solutionType": data.get("solutionType"),
        "solutionComment": data.get("solutionComment"),
        "longitude": data.get("longitude"),
        "latituted" : data.get("latituted"),
        
    }

    actions_collection.insert_one(new_action)
    return jsonify({"status": "success", "message": "Action created successfully", "actionNumber": actionNumber}), 201

# Listar todas las acciones
@action_api.route('/actions/<string:date>', methods=['GET'])
def list_actions(date):
    actions = list(actions_collection.find({"dateAction":date}, {'_id': 0}).sort('dateAction', -1))
    return jsonify(actions), 200

# Obtener una acción específica por número
@action_api.route('/action/<string:actionNumber>', methods=['GET'])
def get_action(actionNumber):
    action = actions_collection.find_one({"actionNumber": actionNumber}, {'_id': 0})
    if action:
        return jsonify(action), 200
    else:
        return jsonify({"status": "failure", "message": "Action not found"}), 404

# Editar una acción existente
@action_api.route('/action/<string:actionNumber>', methods=['PUT'])
def edit_action(actionNumber):
    data = request.json
    if not data:
        return jsonify({"status": "failure", "message": "No data provided"}), 400

    result = actions_collection.update_one(
        {"actionNumber": actionNumber},
        {"$set": data}
    )
    if result.matched_count:
        return jsonify({"status": "success", "message": "Action updated successfully"}), 200
    else:
        return jsonify({"status": "failure", "message": "Action not found"}), 404

# Eliminar una acción
@action_api.route('/action/<string:actionNumber>', methods=['DELETE'])
def delete_action(actionNumber):
    result = actions_collection.delete_one({"actionNumber": actionNumber})
    if result.deleted_count:
        return jsonify({"status": "success", "message": "Action deleted successfully"}), 200
    else:
        return jsonify({"status": "failure", "message": "Action not found"}), 404

@action_api.route('/potentialCustomers', methods=['GET'])
def potentialCustomers():
    customers_cursor = list(potential_customers.find({}, {'_id': 0}))
    return jsonify(customers_cursor), 200
