from flask import Flask, send_file, make_response, request, Response, send_from_directory,Blueprint,jsonify
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from pymongo import MongoClient
from jose import JWTError, jwt
import json
from bson import ObjectId
from functools import wraps
from ..utils import email_utils as emails
user_api = Blueprint('user', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
customers_collection = db['customers']  
users_collection = db['users']  

@user_api.route('/', methods=['GET'])
def get_users():
    return jsonify({"message": "Ruta /api/user funcionando correctamente 🚀"})

@user_api.route('/login', methods=['POST'])
def login():
    # Obtener datos del cuerpo de la solicitud
    data = request.json
    user = data.get('user')
    user = user.strip().lower()
    password = data.get('password')
    if not password or not user:
        return jsonify({'message': 'Missing required fields'}), 400

    bcrypt = Bcrypt()
    user_data = customers_collection.find_one({
        '$or': [
            {'user': user}
        ]
    })  
    if user_data:
        # Verificar la contraseña almacenada en la base de datos con la proporcionada
        hashed_password = user_data.get('password')
        if bcrypt.check_password_hash(hashed_password, password):
            # Generar token JWT con una validez de 1 día
            token_payload = {'user_id': str(user_data['_id']), 'exp': datetime.utcnow() + timedelta(days=90)}
            token = jwt.encode(token_payload, 'Caremonda', algorithm='HS256')
            # Devolver el token junto con los datos del usuario
            user_data['_id'] = str(user_data['_id'])
            user_data.pop('password')
            return jsonify({'message': 'Login successful', 'token': token, 'user_data': user_data}), 200
        else:
            # Contraseña incorrecta
            return jsonify({'message': 'Invalid credentials'}), 401
    else:
        # Usuario no encontrado
        return jsonify({'message': 'User not found'}), 404
@user_api.route('/login_admin', methods=['POST'])
def login_admin():
    data = request.json
    user = data.get('user')
    user = user.strip().lower()
    password = data.get('password')
    if not password or not user:
        return jsonify({'message': 'Missing required fields'}), 400

    bcrypt = Bcrypt()
    user_data = users_collection.find_one({
        '$or': [
            {'user': user}
        ]
    })  
    if user_data:
        # Verificar la contraseña almacenada en la base de datos con la proporcionada
        hashed_password = user_data.get('password')
        if bcrypt.check_password_hash(hashed_password, password):
            # Generar token JWT con una validez de 1 día
            token_payload = {'user_id': str(user_data['_id']), 'exp': datetime.utcnow() + timedelta(days=90)}
            token = jwt.encode(token_payload, 'Caremonda', algorithm='HS256')
            # Devolver el token junto con los datos del usuario
            user_data['_id'] = str(user_data['_id'])
            user_data.pop('password')
            return jsonify({'message': 'Login successful', 'token': token, 'user_data': user_data}), 200
        else:
            # Contraseña incorrecta
            return jsonify({'message': 'Invalid credentials'}), 401
    else:
        # Usuario no encontrado
        return jsonify({'message': 'User not found'}), 404
@user_api.route('/check_token', methods=['POST'])
def check_token():
    token = request.headers.get('Authorization', '').split('Bearer ')[-1]
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        payload = jwt.decode(token, 'Caremonda', algorithms=['HS256'])
        # Verificar si el token ha expirado
        if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
            return jsonify({'message': 'Token has expired'}), 401
        else:
            # Token válido
            return jsonify({'message': 'Token is valid'}), 200
    except JWTError:
        return jsonify({'message': 'Token has expired or Invalid'}), 401

@user_api.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization', '').split('Bearer ')[-1]
    try:
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        payload = jwt.decode(token, 'Caremonda', algorithms=['HS256'])
        # Invalidar el token estableciendo una fecha de expiración pasada
        payload['exp'] = datetime.utcnow() - timedelta(seconds=1)
        invalidated_token = jwt.encode(payload, 'Caremonda', algorithm='HS256')

        return jsonify({'message': 'Logout successful', 'invalidated_token': invalidated_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/change_password', methods=['POST'])
def change_password():
    token = request.headers.get('Authorization', '').split('Bearer ')[-1]
    data = request.json
    new_password = data.get('password')
    
    try:
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        payload = jwt.decode(token, 'Caremonda', algorithms=['HS256'])
        user_id = payload['user_id']

        # Verificar que el usuario exista en la base de datos
        user_data = customers_collection.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            return jsonify({'message': 'User not found'}), 404

        # Actualizar la contraseña del usuario en la base de datos
        bcrypt = Bcrypt()
        new_hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        customers_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': new_hashed_password}})

        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    user = data.get('user')
    
    if not user:
        return jsonify({'message': 'Missing user field'}), 400
    user_data = customers_collection.find_one({'$or': [{'email': user}, {'phone': user}]})
    
    if user_data:
        emails.send_restore_password(user_data)
        return jsonify({'message': 'Se ha enviado un mensaje al correo registrado con instrucciones para restablecer la contraseña'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@user_api.route('/restore', methods=['POST'])
def forgot_change_password():
    data = request.json
    new_password = data.get('password')
    user_id = data.get('user_id')
    try:
        bcrypt = Bcrypt()
        new_hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        customers_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': new_hashed_password}})
        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@user_api.route('/delete_account', methods=['POST'])
def delete_account():
    # Obtener datos del cuerpo de la solicitud
    data = request.json
    email = data.get('user_email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    bcrypt = Bcrypt()
    # Buscar en la colección de clientes por correo electrónico
    user_data = customers_collection.find_one({'email': email})

    if user_data:
        # Verificar la contraseña almacenada en la base de datos con la proporcionada
        hashed_password = user_data.get('password')
        if bcrypt.check_password_hash(hashed_password, password):
            # Eliminar la cuenta de usuario de la base de datos
            customers_collection.delete_one({'email': email})
            return jsonify({'message': 'Account deleted successfully'}), 200
        else:
            # Contraseña incorrecta
            return jsonify({'message': 'Invalid password'}), 401
    else:
        # Usuario no encontrado
        return jsonify({'message': 'User not found'}), 404

@user_api.route('/change_password_admin', methods=['POST'])
def change_password_admin():
    data = request.json
    new_password = data.get('password')
    user_id = data.get('user_id')
    try:
        # Verificar que el usuario exista en la base de datos
        user_data = customers_collection.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            return jsonify({'message': 'User not found'}), 404

        # Actualizar la contraseña del usuario en la base de datos
        bcrypt = Bcrypt()
        new_hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        customers_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': new_hashed_password}})

        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
