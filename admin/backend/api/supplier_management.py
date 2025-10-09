from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId, errors as bson_errors

from ..db import get_db

# Inicialización
db = get_db()
supplier_collection = db['suppliers']
supplier_api = Blueprint('supplier', __name__)

# ---------------------- Listar todos los proveedores ----------------------
@supplier_api.route('/suppliers', methods=['GET'])
def list_suppliers():
    try:
        suppliers = list(supplier_collection.find({}).sort('name', 1))
        for supplier in suppliers:
            supplier['_id'] = str(supplier['_id'])
        return jsonify(suppliers), 200
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500


# ---------------------- Crear nuevo proveedor ----------------------
@supplier_api.route('/supplier', methods=['POST'])
def create_supplier():
    data = request.get_json() or {}

    required_fields = ('name', 'nit', 'email', 'address')
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({
            "status": "failure",
            "message": f"Missing required fields: {', '.join([f for f in required_fields if f not in data])}"
        }), 400

    # Validar duplicado por NIT o correo
    if supplier_collection.find_one({"$or": [{"nit": data["nit"]}, {"email": data["email"]}]}):
        return jsonify({
            "status": "failure",
            "message": "A supplier with this NIT or email already exists."
        }), 409

    supplier = {
        "name": data["name"],
        "nit": data["nit"],
        "email": data["email"],
        "address": data["address"],
        "phone": data.get("phone", ""),
        "typeSupport": data.get("typeSupport", ""),
        "nickname": data.get("nickname", ""),
        "type_transaction": data.get("type_transaction", "Efectivo")
    }

    supplier_collection.insert_one(supplier)
    return jsonify({
        "status": "success",
        "message": "Supplier created successfully."
    }), 201


# ---------------------- Editar proveedor existente ----------------------
@supplier_api.route('/supplier/<string:id>', methods=['PUT'])
def edit_supplier(id):
    try:
        object_id = ObjectId(id)
    except bson_errors.InvalidId:
        return jsonify({"status": "failure", "message": "Invalid supplier ID format."}), 400

    data = request.get_json() or {}
    update_data = {
        "name": data.get("name"),
        "nit": data.get("nit"),
        "email": data.get("email"),
        "address": data.get("address"),
        "phone": data.get("phone"),
        "typeSupport": data.get("typeSupport"),
        "nickname": data.get("nickname"),
        "type_transaction": data.get("type_transaction", "Efectivo")
    }

    # Eliminar campos nulos (para no sobreescribir con None)
    update_data = {k: v for k, v in update_data.items() if v is not None}

    result = supplier_collection.update_one({"_id": object_id}, {"$set": update_data})

    if result.matched_count:
        return jsonify({"status": "success", "message": "Supplier updated successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Supplier not found."}), 404


# ---------------------- Eliminar proveedor ----------------------
@supplier_api.route('/supplier/<string:id>', methods=['DELETE'])
def delete_supplier(id):
    try:
        object_id = ObjectId(id)
    except bson_errors.InvalidId:
        return jsonify({"status": "failure", "message": "Invalid supplier ID format."}), 400

    result = supplier_collection.delete_one({"_id": object_id})
    if result.deleted_count:
        return jsonify({"status": "success", "message": "Supplier deleted successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Supplier not found."}), 404


# ---------------------- Obtener un proveedor por ID ----------------------
@supplier_api.route('/supplier/<string:id>', methods=['GET'])
def get_supplier(id):
    try:
        object_id = ObjectId(id)
    except bson_errors.InvalidId:
        return jsonify({"status": "failure", "message": "Invalid supplier ID format."}), 400

    supplier = supplier_collection.find_one({"_id": object_id})
    if not supplier:
        return jsonify({"status": "failure", "message": "Supplier not found."}), 404

    supplier["_id"] = str(supplier["_id"])
    return jsonify(supplier), 200
