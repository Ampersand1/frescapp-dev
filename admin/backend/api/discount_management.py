from flask import Blueprint, jsonify, request
from ..models.discount import Discount
from datetime import datetime

discount_api = Blueprint('discount', __name__)

@discount_api.route('/discount', methods=['POST'])
def create_discount():
    data = request.get_json()
    code = data.get('code')
    description = data.get('description')
    discount_percentage = data.get('discount_percentage')
    valid_from = data.get('valid_from')
    valid_to = data.get('valid_to')
    customer_email = data.get('customer_email')

    if not code or not discount_percentage or not customer_email:
        return jsonify({'message': 'Missing required fields'}), 400

    existing_discount = Discount.objects(code=code).first()
    if existing_discount:
        return jsonify({'message': 'Discount code already exists'}), 409

    discount = Discount(
        code=code,
        description=description,
        discount_percentage=discount_percentage,
        valid_from=valid_from or datetime.utcnow(),
        valid_to=valid_to,
        customer_email=customer_email
    )
    discount.save()

    return jsonify({'message': 'Discount created successfully'}), 201

@discount_api.route('/discount/<string:discount_code>', methods=['GET'])
def get_discount(discount_code):
    discount = Discount.objects(discount_code=discount_code).first()
    if not discount:
        return jsonify({'message': 'Discount not found'}), 404

    return jsonify({
        'discount_code': discount.discount_code,
        'description': discount.description,
        'value': discount.value,
        'start_date': discount.start_date,
        'end_date': discount.end_date,
        'customer_email': discount.customer_email
    }), 200

@discount_api.route('/discount/<string:discount_code>', methods=['PUT'])
def update_discount(discount_code):
    data = request.get_json()
    discount = Discount.objects(discount_code=discount_code).first()

    if not discount:
        return jsonify({'message': 'Discount not found'}), 404

    discount.update(
        description=data.get('description', discount.description),
        value=data.get('value', discount.value),
        start_date=data.get('start_date', discount.start_date),
        end_date=data.get('end_date', discount.end_date),
        customer_email=data.get('customer_email', discount.customer_email)
    )

    return jsonify({'message': 'Discount updated successfully'}), 200

@discount_api.route('/discount/<string:discount_code>', methods=['DELETE'])
def delete_discount(discount_code):
    discount = Discount.objects(discount_code=discount_code).first()

    if not discount:
        return jsonify({'message': 'Discount not found'}), 404

    discount.delete()
    return jsonify({'message': 'Discount deleted successfully'}), 200

@discount_api.route('/discount/validate', methods=['POST'])
def validate_discount():
    data = request.get_json()
    discount_code = data.get('discount_code')
    customer_email = data.get('customer_email')
    current_date = datetime.utcnow()
    discount = Discount.find_by_customer_email(discount_code=discount_code, customer_email=customer_email)
    if not discount:
        return jsonify({'message': 'Discount not found or not valid for this customer'}), 404

    if discount.start_date and discount.end_date:
        if discount.start_date <= current_date <= discount.end_date:
            return jsonify({
                'discount_code': discount.discount_code,
                'value': discount.value
            }), 200
        else:
            return jsonify({'message': 'Discount is not valid at this time'}), 400
    else:
        return jsonify({'message': 'Discount dates are not properly defined'}), 400
