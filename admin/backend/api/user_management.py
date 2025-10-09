from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from bson import ObjectId
from functools import wraps
from ..utils import email_utils as emails
from backend.db import get_db

# --- CONFIGURACIÓN ---
SECRET_KEY = "Caremonda"  # ⚠️ Reemplázala por variable de entorno en producción
ALGORITHM = "HS256"
TOKEN_EXP_DAYS = 90

# --- BLUEPRINT ---
user_api = Blueprint('user', __name__)
db = get_db()
customers_collection = db['customers']
users_collection = db['users']
bcrypt = Bcrypt()

# --- DECORADOR DE AUTENTICACIÓN ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
        except JWTError:
            return jsonify({"message": "Invalid or expired token"}), 401
        return f(user_id, *args, **kwargs)
    return decorated


# --- RUTAS ---
@user_api.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Ruta /api/user funcionando correctamente 🚀"}), 200


# ------------------- LOGIN CLIENTE -------------------
@user_api.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    user = (data.get('user') or '').strip().lower()
    password = data.get('password')

    if not user or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    user_data = customers_collection.find_one({'user': user})
    if not user_data:
        return jsonify({'message': 'User not found'}), 404

    hashed_password = user_data.get('password')
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token_payload = {'user_id': str(user_data['_id']), 'exp': datetime.utcnow() + timedelta(days=TOKEN_EXP_DAYS)}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    user_data['_id'] = str(user_data['_id'])
    user_data.pop('password', None)

    return jsonify({'message': 'Login successful', 'token': token, 'user_data': user_data}), 200


# ------------------- LOGIN ADMIN -------------------
@user_api.route('/login_admin', methods=['POST'])
def login_admin():
    data = request.json or {}
    user = (data.get('user') or '').strip().lower()
    password = data.get('password')

    if not user or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    user_data = users_collection.find_one({'user': user})
    if not user_data:
        return jsonify({'message': 'User not found'}), 404

    hashed_password = user_data.get('password')
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token_payload = {'user_id': str(user_data['_id']), 'role': 'admin', 'exp': datetime.utcnow() + timedelta(days=TOKEN_EXP_DAYS)}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    user_data['_id'] = str(user_data['_id'])
    user_data.pop('password', None)

    return jsonify({'message': 'Admin login successful', 'token': token, 'user_data': user_data}), 200


# ------------------- CHECK TOKEN -------------------
@user_api.route('/check_token', methods=['POST'])
def check_token():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({'message': 'Token is missing'}), 401
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return jsonify({'message': 'Token is valid'}), 200
    except JWTError:
        return jsonify({'message': 'Token has expired or is invalid'}), 401


# ------------------- LOGOUT -------------------
@user_api.route('/logout', methods=['POST'])
def logout():
    # No se puede invalidar un JWT sin lista de revocación, solo se notifica
    return jsonify({'message': 'Logout successful. (JWT cannot be invalidated server-side)'}), 200


# ------------------- CHANGE PASSWORD -------------------
@user_api.route('/change_password', methods=['POST'])
@token_required
def change_password(user_id):
    data = request.json or {}
    new_password = data.get('password')

    if not new_password:
        return jsonify({'message': 'Missing password'}), 400

    new_hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
    customers_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': new_hashed}})

    return jsonify({'message': 'Password updated successfully'}), 200


# ------------------- FORGOT PASSWORD -------------------
@user_api.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json or {}
    user = data.get('user')

    if not user:
        return jsonify({'message': 'Missing user field'}), 400

    user_data = customers_collection.find_one({'$or': [{'email': user}, {'phone': user}]})
    if not user_data:
        return jsonify({'message': 'User not found'}), 404

    emails.send_restore_password(user_data)
    return jsonify({'message': 'Se ha enviado un mensaje al correo con instrucciones para restablecer la contraseña'}), 200


# ------------------- RESTORE PASSWORD -------------------
@user_api.route('/restore', methods=['POST'])
def restore_password():
    data = request.json or {}
    new_password = data.get('password')
    user_id = data.get('user_id')

    if not (new_password and user_id):
        return jsonify({'message': 'Missing required fields'}), 400

    new_hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
    customers_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': new_hashed}})

    return jsonify({'message': 'Password updated successfully'}), 200


# ------------------- DELETE ACCOUNT -------------------
@user_api.route('/delete_account', methods=['POST'])
def delete_account():
    data = request.json or {}
    email = data.get('user_email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    user_data = customers_collection.find_one({'email': email})
    if not user_data:
        return jsonify({'message': 'User not found'}), 404

    hashed_password = user_data.get('password')
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({'message': 'Invalid password'}), 401

    customers_collection.delete_one({'email': email})
    return jsonify({'message': 'Account deleted successfully'}), 200


# ------------------- ADMIN PASSWORD CHANGE -------------------
@user_api.route('/change_password_admin', methods=['POST'])
def change_password_admin():
    data = request.json or {}
    new_password = data.get('password')
    user_id = data.get('user_id')

    if not (new_password and user_id):
        return jsonify({'message': 'Missing required fields'}), 400

    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user_data:
        return jsonify({'message': 'User not found'}), 404

    new_hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
    users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': new_hashed}})

    return jsonify({'message': 'Admin password updated successfully'}), 200
