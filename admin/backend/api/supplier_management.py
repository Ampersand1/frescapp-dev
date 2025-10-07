from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

supplier_api = Blueprint('supplier', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
supplier_collection = db['suppliers']

# Ruta para listar todos los proveedores
@supplier_api.route('/suppliers', methods=['GET'])
def list_suppliers():
    suppliers = list(supplier_collection.find({}).sort('name', 1))
    
    # Convertir ObjectId a string
    for supplier in suppliers:
        supplier['_id'] = str(supplier['_id'])
    
    return jsonify(suppliers), 200

# Ruta para crear un nuevo proveedor
@supplier_api.route('/supplier', methods=['POST'])
def create_supplier():
    data = request.json
    if not all(k in data for k in ('name', 'nit', 'email', 'address')):
        return jsonify({"status": "failure", "message": "Missing fields in request."}), 400
    
    supplier = {
        "name": data['name'],
        "nit": data['nit'],
        "email": data['email'],
        "address": data['address'],
        "phone": data['phone'],
        "typeSupport" : data['typeSupport'],
        "nickname" : data['nickname'],
        "type_transaction": data.get('type_transaction', 'Efectivo')  # Valor por defecto si no se proporciona
    }
    
    supplier_collection.insert_one(supplier)
    return jsonify({"status": "success", "message": "Supplier created successfully."}), 201

# Ruta para editar un proveedor existente
@supplier_api.route('/supplier/<string:id>', methods=['PUT'])
def edit_supplier(id):
    data = request.json   
    supplier = {
        "name": data['name'],
        "nit": data['nit'],
        "email": data['email'],
        "address": data['address'],
        "phone": data['phone'],
        "typeSupport" : data['typeSupport'],
        "nickname" : data['nickname'],
        "type_transaction": data.get('type_transaction', 'Efectivo')  # Valor por defecto si no se proporciona
    }
    result = supplier_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": supplier}
    )
    
    if result.matched_count:
        return jsonify({"status": "success", "message": "Supplier updated successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Supplier not found."}), 404

# Ruta para eliminar un proveedor
@supplier_api.route('/supplier/<string:id>', methods=['DELETE'])
def delete_supplier(id):
    object_id = ObjectId(id)
    result = supplier_collection.delete_one({"_id": object_id})
    if result.deleted_count:
        return jsonify({"status": "success", "message": "Supplier deleted successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Supplier not found."}), 404
