from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime
from ..db import get_db  # Asumiendo que tienes tu función get_db() en db.py

admin_api = Blueprint("admin_api", __name__)

@admin_api.route("/api/admin/create", methods=["POST"])
def create_admin():
    try:
        db = get_db()  # Conexión a MongoDB

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        # Validar campos obligatorios
        required_fields = ["name", "email", "user", "password", "phone"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Generar hash de la contraseña si no viene ya en hash bcrypt
        hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256", salt_length=12)

        # Crear documento con la estructura correcta
        admin_doc = {
            "phone": data["phone"],
            "name": data["name"],
            "email": data["email"],
            "status": "active",
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "password": hashed_password,
            "user": data["user"],
            "role": ["administrador"]
        }

        result = db["users"].insert_one(admin_doc)

        return jsonify({
            "status": "ok",
            "message": "Admin user created successfully",
            "user_id": str(result.inserted_id)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
