from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from bson import json_util
from ..models.cost import Cost

cost_api = Blueprint('cost', __name__)

# ==============================
# 📘 Crear un nuevo costo
# ==============================
@cost_api.route('/cost', methods=['POST'])
def create_cost():
    try:
        data = request.get_json()
        cost = Cost(
            typeCost=data.get('typeCost'),
            detail=data.get('detail'),
            amount=data.get('amount'),
            typePeriod=data.get('typePeriod'),
            period=data.get('period')
        )
        cost.save()
        return jsonify({"status": "success", "message": "Cost saved successfully."}), 201

    except Exception as e:
        current_app.logger.error(f"Error creating cost: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================
# 📘 Listar todos los costos
# ==============================
@cost_api.route('/cost', methods=['GET'])
def list_costs():
    try:
        costs = Cost.objects()
        costs_data = [
            {
                "id": str(cost["_id"]),
                "typeCost": cost.get("typeCost"),
                "detail": cost.get("detail"),
                "amount": cost.get("amount"),
                "typePeriod": cost.get("typePeriod"),
                "period": cost.get("period")
            }
            for cost in costs
        ]
        return jsonify(costs_data), 200

    except Exception as e:
        current_app.logger.error(f"Error listing costs: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================
# ✏️ Editar un costo existente
# ==============================
@cost_api.route('/cost', methods=['PUT'])
def edit_cost():
    try:
        data = request.get_json()
        cost = Cost(
            id=data.get('id'),
            typeCost=data.get('typeCost'),
            detail=data.get('detail'),
            amount=data.get('amount'),
            typePeriod=data.get('typePeriod'),
            period=data.get('period')
        )
        cost.update()
        return jsonify({"status": "success", "message": "Cost updated successfully."}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating cost: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================
# ❌ Eliminar un costo
# ==============================
@cost_api.route('/cost/<string:cost_id>', methods=['DELETE'])
def delete_cost(cost_id):
    try:
        cost = Cost.object(cost_id)
        if not cost:
            return jsonify({"status": "error", "message": "Cost not found."}), 404

        cost_data = Cost(
            id=str(cost.get('_id')),
            typeCost=cost.get('typeCost'),
            detail=cost.get('detail'),
            amount=cost.get('amount'),
            typePeriod=cost.get('typePeriod'),
            period=cost.get('period')
        )
        cost_data.deleteCost()
        return jsonify({"status": "success", "message": "Cost deleted successfully."}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting cost: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
