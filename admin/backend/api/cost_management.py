from flask import Blueprint, jsonify, request
from ..models.route import Route
from pymongo import MongoClient
from datetime import datetime
from werkzeug.utils import secure_filename
import os,json
from werkzeug.utils import secure_filename
from flask import send_from_directory
from models.cost import Cost
from bson import json_util

cost_api = Blueprint('cost', __name__)

@cost_api.route('/cost', methods=['POST'])
def create_cost():
    data = request.json
    cost  = Cost(typeCost = data.get('typeCost'),detail = data.get('detail'),
        amount = data.get('amount'),
        typePeriod = data.get('typePeriod'),
        period = data.get('period'))
    cost.save()
    return jsonify({"status": "success", "message": "Cost saved."}), 200

@cost_api.route('/cost', methods=['GET'])
def list_costs():
    costs = Cost.objects()
    costs_data = [
        {
            "id": str(cost["_id"]),
            "typeCost": cost["typeCost"],
            "detail": cost["detail"],
            "amount": cost["amount"],
            "typePeriod": cost["typePeriod"],
            "period": cost["period"]
        }
        for cost in costs
    ]   
    return jsonify(costs_data), 200

@cost_api.route('/cost', methods=['PUT'])
def edit_cost():
    data = request.json
    cost  = Cost(id = data.get('id') , typeCost = data.get('typeCost'),detail = data.get('detail'),
        amount = data.get('amount'),
        typePeriod = data.get('typePeriod'),
        period = data.get('period'))
    cost.update()
    return jsonify({"status": "success", "message": "Cost updated successfully."}), 200

@cost_api.route('/cost/<string:cost_id>', methods=['DELETE'])
def delete_cost(cost_id):
    cost = Cost.object(cost_id)
    cost_data  = Cost(id = cost.get('id') , typeCost = cost.get('typeCost'),detail = cost.get('detail'),
        amount = cost.get('amount'),
        typePeriod = cost.get('typePeriod'),
        period = cost.get('period'))
    cost_data.deleteCost()
    return jsonify({"status": "success", "message": "Cost deleted successfully."}), 200
    