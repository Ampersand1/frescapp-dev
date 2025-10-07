from flask import Blueprint, jsonify, request
from models.customer import Customer
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime
import utils.email_utils as emails

customer_api = Blueprint('customer', __name__)

# Ruta para crear un nuevo usuario
@customer_api.route('/customer', methods=['POST'])
def create_customer():
    data = request.get_json()
    phone = data.get('phone')
    name = data.get('name')
    document = data.get('document')
    document_type = data.get('document_type')
    address = data.get('address')
    restaurant_name = data.get('restaurant_name')
    email = data.get('email')  
    status = data.get('status')  
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    password = data.get('password')
    category = data.get('category')
    user = data.get('user', email )
    bcrypt = Bcrypt()
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    if not phone or not email:
        return jsonify({'message': 'Faltan campos por diligenciar'}), 400

    if Customer.find_by_email(email=email):
        return jsonify({'message': 'Correo electrónico ya está asociado a otro cliente.'}), 400

    customer = Customer(        
        phone = phone,
        name = name,
        document = document,
        document_type = document_type,
        address = address,
        restaurant_name = restaurant_name,
        email = email,
        status = status,
        created_at = created_at,
        updated_at = updated_at,
        password = hashed_password,
        category = category,
        list_products = "",
        role = "Cliente",
        user = user
    )
    customer.save()
    message = """
                <!DOCTYPE html>
            <html lang="es" style="height: 100%; position: relative;" height="100%">

            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <meta content="width=device-width, initial-scale=1.0" name="viewport">
                <title>Frescapp</title>
            </head>

            <body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0"
                class="kt-woo-wrap order-items-normal k-responsive-normal title-style-none email-id-new_order"
                style="height: 100%; position: relative; background-color: #f7f7f7; margin: 0; padding: 0;" height="100%"
                backgound-color="#f7f7f7">
                <div id="wrapper" dir="ltr"
                    style="background-color: #f7f7f7; margin: 0; padding: 70px 0 70px 0; width: 100%; padding-top: 70px; padding-bottom: px; -webkit-text-size-adjust: none;"
                    backgound-color="#f7f7f7" width="100%">
                    <table cellpadding="0" cellspacing="0" height="100%" width="100%">
                        <tr>
                            <td text-align="center" vtext-align="top">
                                <table id="template_header_image_container" style="width: 100%; background-color: transparent;"
                                    width="100%" backgound-color="transparent">
                                    <tr id="template_header_image">
                                        <td text-align="center" vtext-align="middle">
                                            <table cellpadding="0" cellspacing="0" width="100%" id="template_header_image_table">
                                                <tr>
                                                    <td text-align="center" vtext-align="middle"
                                                        style="text-text-align: center; padding-top: 0px; padding-bottom: 0px;">
                                                        <p style="margin-bottom: 0; margin-top: 0;"><a
                                                                href="https://www.buyfrescapp.com" target="_blank"
                                                                style="font-weight: normal; color: #97d700; display: block; text-decoration: none;"><img
                                                                    src="https://app.buyfrescapp.com:5000/api/shared/banner1.png"
                                                                    alt="Frescapp" width="600"
                                                                    style="border: none; display: inline; font-weight: bold; height: auto; outline: none; text-decoration: none; text-transform: capitalize; font-size: 14px; line-height: 24px; max-width: 100%; width: 600px;"></a>
                                                        </p>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                <table cellpadding="0" cellspacing="0" width="600" id="template_container"
                                    style="background-color: #fff; overflow: hidden; border-style: solid; border-width: 1px; border-right-width: px; border-bottom-width: px; border-left-width: px; border-color: #dedede; border-radius: 3px; box-shadow: 0 1px 4px 1px rgba(0,0,0,.1);"
                                    backgound-color="#fff">
                                    <tr>
                                        <td text-align="center" vtext-align="top">
                                            <!-- Header -->
                                            <table cellpadding="0" cellspacing="0" width="100%" id="template_header"
                                                style='border-bottom: 0; font-weight: bold; line-height: 100%; vertical-text-align: middle; font-family: "Helvetica Neue",Helvetica,Roboto,Arial,sans-serif; background-color: #97d700; color: #fff;'
                                                backgound-color="#97d700">
                                                <tr>
                                                    <td id="header_wrapper"
                                                        style="padding: 36px 48px; display: block; text-text-align: left; padding-top: px; padding-bottom: px; padding-left: 48px; padding-right: 48px;"
                                                        text-align="left">
                                                        <h1>Hola """+str(data.get('name'))+"""!</h1><br>
                                                        <h1
                                                            style='margin: 0; text-text-align: left; font-size: 30px; line-height: 40px; font-family: "Helvetica Neue",Helvetica,Roboto,Arial,sans-serif; font-style: normal; font-weight: 300; color: #fff;'>
                                                            Desde el equipo de Frescapp te damos la bienvenida a la plataforma que te ayudará a optimizar tus compras y crecer juntos.
                                                        </h1>
                                                    </td>
                                                </tr>
                                            </table>
                                            <!-- End Header -->
                                        </td>
                                    </tr>
                                </table> <!-- End template container -->
                            </td>
                        </tr>
                    </table>
                </div>
            </body>

            </html>
    """
    subject = 'Bienvenido a Frescapp!!'
    emails.send_new_account(subject, message, data.get('email'))
    return jsonify({'message': 'Customer created successfully'}), 201

# Ruta para actualizar un usuario existente
@customer_api.route('/customers/<string:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    phone = data.get('phone')
    name = data.get('name')
    document = data.get('document')
    document_type = data.get('document_type')
    address = data.get('address')
    restaurant_name = data.get('restaurant_name')
    email = data.get('email')  
    status = data.get('status')  
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    category = data.get('category')
    role = data.get('role')
    customer = Customer.object(customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    customer.id = customer_id
    customer.phone = phone or customer.phone
    customer.name = name or customer.name
    customer.document = document or customer.document
    customer.document_type = document_type or customer.document_type
    customer.address = address or customer.address
    customer.restaurant_name = restaurant_name or customer.restaurant_name
    customer.email = email or customer.email
    customer.status =status or customer.status
    customer.created_at = created_at or customer.created_at
    customer.updated_at = updated_at or customer.updated_at
    customer.category = category or customer.category
    customer.role = role or customer.role
    customer.updated()
    return jsonify({'message': 'customer updated successfully'}), 200

@customer_api.route('/customers', methods=['GET'])
def list_customers():
    customers_cursor = Customer.objects()
    customer_data = [
        {
            "id": str(customer.get("_id", "")), 
            "phone": customer.get("phone", ""), 
            "name": customer.get("name", ""), 
            "document": customer.get("document", ""), 
            "document_type": customer.get("document_type", ""), 
            "address": customer.get("address", ""), 
            "restaurant_name": customer.get("restaurant_name", ""), 
            "email": customer.get("email", ""), 
            "status": customer.get("status", ""), 
            "created_at": customer.get("created_at", ""), 
            "updated_at": customer.get("updated_at", ""), 
            "category": customer.get("category", ""), 
            "list_products": customer.get("list_products", []),
            "segmentation": customer.get("segmentation", ""),
            "role": customer.get("role", "")
        }
        for customer in customers_cursor
    ]
    customers_json = json.dumps(customer_data)
    return customers_json, 200
@customer_api.route('/customer/<string:customer_id>', methods=['GET'])
def customer(customer_id):
    customer_object = Customer.object(customer_id)
    if customer_object:
        customer_json = {
            "phone": customer_object.phone,
            "name": customer_object.name,
            "document": customer_object.document,
            "document_type": customer_object.document_type,
            "address": customer_object.address,
            "restaurant_name": customer_object.restaurant_name,
            "email": customer_object.email,
            "status": customer_object.status,
            "created_at": str(customer_object.created_at),
            "updated_at": str(customer_object.updated_at),
            "category": customer_object.category,
            "list_products" : customer_object.list_products
        }
        return jsonify(customer_json), 200
    else:
        return jsonify({'message': 'Customer not found'}), 404