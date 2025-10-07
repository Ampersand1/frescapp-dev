from flask import Blueprint, jsonify, request, send_file, Response
from models.order import Order
import json
from flask_bcrypt import Bcrypt
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import locale
from flask import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from io import BytesIO
from utils.email_utils import send_new_order
from io import StringIO
import csv
from models.product import Product
from models.customer import Customer
from models.route import Route
import os,re


order_api = Blueprint('order', __name__)

@order_api.route('/order', methods=['POST'])
@order_api.route('/order/<string:order_number>', methods=['POST'])
def create_order(order_number=None):
    data = request.get_json()
    id = data.get('id', None)
    order_number = data.get('order_number', order_number)
    customer_email = data.get('email') or data.get('customer_email') or ''
    customer_phone = data.get('phoneNumber') or data.get('customer_phone')  or ''
    customer_documentNumber = data.get('documentNumber') or data.get('customer_documentNumber') or ''
    customer_documentType = data.get('documentType') or data.get('customer_documentType') or ''
    customer_name = data.get('customerName') or data.get('customer_name')  or ''
    delivery_date = data.get('deliveryDate') or data.get('delivery_date') or ''
    status = data.get('status') or 'Creada'
    created_at = data.get('created_at', None)
    updated_at = data.get('updated_at', None)
    products = data.get('products', [])
    total = data.get('total', 0.0)
    paymentMethod = data.get('paymentMethod', 'Cash')
    deliveryAddress = data.get('deliveryAddress', 'Default Address')
    deliveryAddressDetails = data.get('deliveryAddressDetails') or ''
    deliveryCost = data.get('deliveryCost', 0.0)
    discount = data.get("discount", 0.0)
    alegra_id = data.get('alegra_id','000')
    deliverySlot = data.get('deliverySlot', '09:00-12:00')
    open_hour = data.get('open_hour', '')
    payment_date = data.get('payment_date', delivery_date) 
    driver_name = data.get('driver_name', '')
    seller_name = data.get('seller_name', '')
    source = data.get('source', 'Aplicación')
    totalPayment = 0.0
    status_payment = data.get('status_payment', 'Pendiente') or 'Pendiente'
    if not customer_email or not delivery_date:
        return jsonify({'message': 'Missing required fields'}), 400
    customer = Customer.find_by_email(customer_email)
    try:
        open_hour_customer = customer.get('open_hour','') or ''
    except:
        open_hour_customer  =''
    order = Order(      
        id = id,  
        order_number = order_number,
        customer_email = customer_email,
        customer_phone = customer_phone,
        customer_documentNumber = customer_documentNumber.split('-')[0],
        customer_documentType = customer_documentType,
        customer_name = customer_name.capitalize(),
        delivery_date = delivery_date,
        status = status,
        created_at = created_at,
        updated_at = updated_at,
        products = products,
        total = total,
        deliverySlot = deliverySlot,
        paymentMethod = paymentMethod,
        deliveryAddress = deliveryAddress,
        deliveryAddressDetails = deliveryAddressDetails,
        deliveryCost = deliveryCost,
        discount=discount,
        alegra_id = alegra_id,
        open_hour=open_hour_customer,
        payment_date=payment_date,
        driver_name=driver_name,
        seller_name=seller_name,
        source=source,
        totalPayment=0.0,
        status_payment=status_payment
    )
    finded_order = Order.find_by_order_number(order_number=order_number)
    ruta = Route.find_by_date(delivery_date)
    if finded_order:
        order.updated()
    else:
        order.save()
        send_order_email(order_number, customer_email, delivery_date, products, total)
    if ruta:
        for stop in ruta.get('stops'):
            if stop["order_number"] == order_number:
                stop["total_charged"] = sum(item['price_sale'] * item['quantity'] for item in order.products)
                stop["total_to_charge"] = sum(item['price_sale'] * item['quantity'] for item in order.products)
                stop["quantity_sku"] = len(order.products)
                stop["payment_method"] = order.paymentMethod
                stop["payment_date"] = order.payment_date
                stop["address"] = order.deliveryAddress
                stop["driver_name"] = order.driver_name
        route_exist = Route(
            id=ruta['id'],
            route_number=ruta.get('route_number'),
            close_date=ruta.get('close_date'),
            cost=ruta.get('cost'),
            stops=ruta.get('stops')
        )
        route_exist.update()
    return jsonify({'message': 'Order created successfully'}), 201
@order_api.route('/order/<string:id>', methods=['DELETE'])
def delete_order(id=None):
    # Buscar la orden por su ID
    finded_order = Order.object(id)
    if not finded_order:
        return jsonify({'message': 'Order not found'}), 404

    # Buscar la ruta asociada a la fecha de entrega de la orden
    ruta = Route.find_by_date(finded_order.delivery_date)
    if ruta:
        # Filtrar los stops para eliminar el que coincide con el número de orden
        ruta['stops'] = [stop for stop in ruta.get('stops', []) if stop.get("order_number") != finded_order.order_number]

        # Actualizar la ruta en la base de datos
        route_exist = Route(
            id=ruta['id'],
            route_number=ruta.get('route_number'),
            close_date=ruta.get('close_date'),
            cost=ruta.get('cost'),
            stops=ruta.get('stops')
        )
        route_exist.update()

    # Eliminar la orden
    finded_order.delete_order()

    return jsonify({'message': 'Order deleted successfully'}), 200
@order_api.route('/orders/<string:startDate>/<string:endDate>', methods=['GET'])
def list_orders(startDate,endDate):
    orders_cursor = Order.find_by_date(startDate,endDate)
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"] if order["order_number"] else order["orderNumber"], 
         "customer_email": order["customer_email"] if order["customer_email"] else order["customerEmail"], 
         "customer_phone": order["customer_phone"] if order["customer_phone"] else order["customerPhone"], 
        "customer_documentNumber": order.get("customer_documentNumber", order.get("customerDocumentNumber", "N/A")),
        "customer_documentType": order.get("customer_documentType", order.get("customerDocumentType", "N/A")),
         "customer_name": order["customer_name"] if order["customer_name"] else order["customerName"], 
         "delivery_date": order["delivery_date"] if order["delivery_date"] else order["deliveryDate"], 
         "status": order["status"], 
         "status_payment": order.get("status_payment", "Pendiente"),
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"],
         "total": order["total"], 
         "deliverySlot": order["deliverySlot"], 
         "paymentMethod": order["paymentMethod"],
         "deliveryAddress": order["deliveryAddress"], 
         "deliveryAddressDetails": order["deliveryAddressDetails"] ,
         "alegra_id" :order["alegra_id"],
         "open_hour" : order["open_hour"],
         "driver_name" : order["driver_name"],
         "seller_name" : order["seller_name"],
         "source" : order["source"],
         "totalPayment" : order["totalPayment"]
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200
@order_api.route('/orders/status/<string:status>', methods=['GET'])
def list_ordersByStats(status):
    orders_cursor = Order.find_by_status_payment(status)
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"] if order["order_number"] else order["orderNumber"], 
         "customer_email": order["customer_email"] if order["customer_email"] else order["customerEmail"], 
         "customer_phone": order["customer_phone"] if order["customer_phone"] else order["customerPhone"], 
        "customer_documentNumber": order.get("customer_documentNumber", order.get("customerDocumentNumber", "N/A")),
        "customer_documentType": order.get("customer_documentType", order.get("customerDocumentType", "N/A")),
         "customer_name": order["customer_name"] if order["customer_name"] else order["customerName"], 
         "delivery_date": order["delivery_date"] if order["delivery_date"] else order["deliveryDate"], 
         "status": order["status"], 
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"],
         "total": order["total"], 
         "deliverySlot": order["deliverySlot"], 
         "paymentMethod": order["paymentMethod"],
         "deliveryAddress": order["deliveryAddress"], # Nuevo campo: Dirección de entrega
         "deliveryAddressDetails": order["deliveryAddressDetails"],
        "alegra_id" :order["alegra_id"],
        "totalPayment" : order["totalPayment"],
        "open_hour" : order["open_hour"],
        "driver_name" : order["driver_name"],
        "seller_name" : order["seller_name"],
        "source" : order["source"]
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200
@order_api.route('/generate_pdf/<string:id_order>', methods=['GET'])
def generate_remision(id_order):
    order = Order.object(id_order)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    buffer = BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=28.35,
        rightMargin=28.35,
        topMargin=28.35,
        bottomMargin=28.35
    )

    styles = getSampleStyleSheet()
    image_path = 'https://buyfrescapp.com/images/banner1.png'
    logo = Image(image_path, width=95, height=50)
    pdf_content = []
    remision_number = order.order_number
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    # Datos de la orden
    order_data = [
        [logo, 'Remisión #', order.order_number, 'Fecha', order.delivery_date],
        ['', 'Nombre', Paragraph(order.customer_name, word_wrap_style), 'Teléfono del Cliente', Paragraph(order.customer_phone, word_wrap_style)],
        ['', 'Método de pago', Paragraph(order.paymentMethod, word_wrap_style), 'Horario de entrega', Paragraph(order.deliverySlot + ' (' + order.open_hour + ')', word_wrap_style)],
        ['Dirección de entrega', Paragraph(order.deliveryAddress, word_wrap_style),  'Detalle de entrega', Paragraph(order.deliveryAddressDetails, word_wrap_style),'']
    ]

    order_table = Table(order_data, colWidths=[100, 100, 150, 100, 100])
    order_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (0, 2)),  # Logo 3 filas
        ('VALIGN', (0, 0), (0, 2), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 2), 'CENTER'),
        # Dirección: valor solo en columna 2
        ('SPAN', (1, 3), (1, 3)),

        # Detalle: valor ocupa columnas 4 y 5
        ('SPAN', (3, 3), (4, 3)),


        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black)
    ]))

    pdf_content.append(order_table)
    pdf_content.append(Spacer(1, 20))
    table_width = 550


    # Aplicar estilos de WordWrap
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    product_data = [
        ['SKU', 'Nombre', 'Cantidad', 'Precio Unitario', 'Total'],  # Encabezado
    ]
    for product in sorted(list(order.products), key=lambda x: x['name']):
        sku = product['sku']
        name = product['name']
        quantity = product['quantity']
        price_sale = locale.format_string('%.2f', round(product.get('price_sale'),0), grouping=True)
        total = locale.format_string('%.2f', round(float(product.get('price_sale')) * float(quantity),0), grouping=True)
        name_paragraph = Paragraph(name, word_wrap_style)
        product_row = [sku, name_paragraph, str(quantity)  + "  " + str(product.get('unit', '')), price_sale, total]
        product_data.append(product_row)

    subtotal = sum(round(float(product['quantity']) * float(product['price_sale']),0) for product in list(order.products))
    try:
        descuentos = float(order.discount)
    except:
        descuentos = 0    
    total = subtotal - descuentos
    subtotal_formatted = locale.format_string('%.2f', subtotal, grouping=True)
    descuentos_formatted = locale.format_string('%.2f', descuentos, grouping=True)
    total_formatted = locale.format_string('%.2f', total, grouping=True)
    image_path_payment = 'https://buyfrescapp.com/images/medio_pago.png'  # URL o ruta local de la imagen del medio de pago
    payment_image = Image(image_path_payment, width=290, height=100)  # Ajustar tamaño de la imagen
    product_data.extend([[payment_image,'','','',''],
        ['', '', '', 'Subtotal', subtotal_formatted],
        ['', '', '', 'Descuentos', descuentos_formatted],
        ['', '', '', 'Total', total_formatted]
    ])


    product_table = Table(product_data, colWidths=[120,200,80,80,80])
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),  # Color de fondo del encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Bordes internos
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),  # Borde externo
        ('SPAN', (0, len(order.products)+1), (2, len(order.products)+4))

    ]))
    pdf_content.append(product_table)

    # Generar el PDF
    pdf.build(pdf_content)

    # Mover el cursor del buffer al inicio
    buffer.seek(0)

    # Crear una respuesta con el archivo PDF y establecer el encabezado Content-Disposition
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=Orden_{}.pdf'.format(remision_number)
    return response

@order_api.route('/orders_customer/<string:email>', methods=['GET'])
def list_orders_customer(email):
    orders_cursor = Order.find_by_customer(email)
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"] if order["order_number"] else order["orderNumber"], 
         "customer_email": order["customer_email"] if order["customer_email"] else order["customerEmail"], 
         "customer_phone": order["customer_phone"] if order["customer_phone"] else order["customerPhone"], 
         "customer_documentNumber": order["customer_documentNumber"] if order["customer_documentNumber"] else order["customerDocumentNumber"], 
         "customer_documentType": order["customer_documentType"] if order["customer_documentType"] else order["customerDocumentType"], 
         "customer_name": order["customer_name"] if order["customer_name"] else order["customerName"], 
         "delivery_date": order["delivery_date"] if order["delivery_date"] else order["deliveryDate"], 
         "status": order["status"], 
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"],
         "total": order["total"], 
         "deliverySlot": order["deliverySlot"], 
         "paymentMethod": order["paymentMethod"], 
         "deliveryAddress": order['deliveryAddress'],
         "deliveryAddressDetails" : order['deliveryAddressDetails'],
            "alegra_id" :order["alegra_id"]
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200

@order_api.route('/orders_latest_customer/<string:email>', methods=['GET'])
def orders_latest_customer(email):
    # Encuentra las órdenes del cliente por su correo electrónico y ordénalas por delivery_date en orden descendente
    orders_cursor = Order.find_by_customer(email).sort("delivery_date", -1).limit(3)
    
    order_data = [
        {
            "id": str(order["_id"]), 
            "order_number": order.get("order_number", order.get("orderNumber")), 
            "customer_email": order.get("customer_email", order.get("customerEmail")), 
            "customer_phone": order.get("customer_phone", order.get("customerPhone")), 
            "customer_documentNumber": order.get("customer_documentNumber", order.get("customerDocumentNumber")), 
            "customer_documentType": order.get("customer_documentType", order.get("customerDocumentType")), 
            "customer_name": order.get("customer_name", order.get("customerName")), 
            "delivery_date": order.get("delivery_date", order.get("deliveryDate")), 
            "status": order["status"], 
            "created_at": order["created_at"], 
            "updated_at": order["updated_at"], 
            "products": order["products"],
            "total": order["total"], 
            "deliverySlot": order["deliverySlot"], 
            "paymentMethod": order["paymentMethod"], 
            "deliveryAddress": order['deliveryAddress'],
            "deliveryAddressDetails": order['deliveryAddressDetails']
        }
        for order in orders_cursor
    ]
    
    orders_json = json.dumps(order_data)
    return orders_json, 200


def send_order_email(order_number, customer_email, delivery_date, products, total):
    subject = f'Orden confirmada - Orden #{order_number}'
    orden = Order.find_by_order_number(order_number)
    # Construir la lista de productos en HTML
    product_list_html = ""
    for product in products:
        subtotal = product['quantity'] * float(product['price_sale'])
        price_formatted = f'{float(product["price_sale"]):,.2f}'  
        subtotal_formatted = f'{subtotal:,.2f}'  #
        product_list_html += f"<tr><td>{product['name']}</td><td style='text-align: center;'>{product['quantity']}</td><td style='text-align: center;'>{price_formatted}</td><td style='text-align: center;'>{subtotal_formatted}</td></tr>"
    
    # Construir el mensaje HTML completo
    html_message = f"""
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
            style="background-color: #f7f7f7; margin: 0; padding: 70px 0 70px 0; width: 100%; padding-top: 70px; padding-bottom: px; -webkit-text-size-adjust: none; "
            backgound-color="#f7f7f7" width="100%" text-align="center">
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
                                                style="padding: 36px 48px; text-align: left; background-color: #97D700; color: white; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5;">
                                                <p style="margin: 0; font-size: 18px; font-weight: bold;">Hola</p>
                                                <p style="margin: 8px 0; font-size: 22px; font-weight: bold;">{orden.customer_name},</p>
                                                <p style="margin: 8px 0;">Hemos recibido tu nueva orden y será entregada el {delivery_date} en {orden.deliveryAddress} entre {orden.deliverySlot}.</p>
                                                <p style="margin: 8px 0;">Será un gusto entregarla. Gracias</p>
                                            </td>
                                        </tr>
                                    </table>
                                    <!-- End Header -->
                                    <!-- Products List -->
                                    <table cellpadding="0" cellspacing="0" width="100%" id="template_product_list"
                                        style="font-family: 'Helvetica Neue',Helvetica,Roboto,Arial,sans-serif; font-size: 14px; line-height: 24px; color: #333; width: 100%;"
                                        backgound-color="#ffffff">
                                        <tr>
                                            <th>Producto</th>
                                            <th style="text-align: center;">Cantidad</th>
                                            <th style="text-align: center;">Precio Unitario</th>
                                            <th style="text-align: center;">Subtotal</th>
                                        </tr>
                                        {product_list_html}
                                    </table>
                                    <!-- End Products List -->
                                    <!-- Total -->
                                    <p style="text-align: right;"><b>Total: </b>{total:,.2f}</p>
                                    <!-- End Total -->
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
    
    # Envía el correo
    send_new_order(subject, html_message, customer_email)

@order_api.route('/orders/csv', methods=['GET'])
def download_orders_csv():
    # Obtener todas las órdenes
    orders_cursor = Order.objects()

    # Crear un objeto StringIO para escribir el CSV en memoria
    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)

    # Escribir la cabecera del CSV
    csv_writer.writerow([
        "Order ID"
        , "Order Number"
        , "Customer Email"
        , "Customer Phone"
        ,"Customer Document Number"
        , "Customer Document Type"
        , "Customer Name"
        ,"Delivery Date"
        , "Status"
        , "Created At"
        , "Updated At"
        , "Total"
        , "Delivery Slot"
        , "Payment Method"
       , "Delivery Address"
        , "Delivery Address Details"
        ,"Product SKU"
        , "Product Name"
        , "Product Description"
        , "Product Quantity"
        ,"Product Price Sale"
        , "Product Price Purchase"
        , "Product Category"
        , "Product Root"
        , "Product Child"
        , "Product Discount"
        , "Product Margen"
        , "Product IVA"
        , "Product IVA Value"
        , "Product Status"
        , "Product Proveedor"
        , "Product Step Unit"
    ])

    # Escribir los datos de las órdenes y productos
    for order in orders_cursor:
        order_id = str(order["_id"])
        order_number = order["order_number"] if order["order_number"] else order["orderNumber"]
        customer_email = order["customer_email"] if order["customer_email"] else order["customerEmail"]
        customer_phone = order["customer_phone"] if order["customer_phone"] else order["customerPhone"]
        customer_document_number = order.get("customer_documentNumber", order.get("customerDocumentNumber", "N/A"))
        customer_document_type = order.get("customer_documentType", order.get("customerDocumentType", "N/A"))
        customer_name = order["customer_name"] if order["customer_name"] else order["customerName"]
        delivery_date = order["delivery_date"] if order["delivery_date"] else order["deliveryDate"]
        status = order["status"]
        created_at = order["created_at"]
        updated_at = order["updated_at"]
        total = order["total"]
        delivery_slot = order["deliverySlot"]
        payment_method = order["paymentMethod"]
        delivery_address = order["deliveryAddress"]
        delivery_address_details = order["deliveryAddressDetails"]

        for product in order["products"]:
            product_sku = product.get("sku", "")
            product_quantity = product.get("quantity", "")
            product_price_sale = product.get("price_sale", "")
            
            # Buscar el producto en la colección de productos usando el SKU
            product_data = Product.find_by_sku(sku=product_sku)
            if product_data:
                product_name = product_data["name"]
                product_description = product_data["description"]
                product_price_purchase = product_data["price_purchase"]
                product_category = product_data["category"]
                product_root = product_data["root"]
                product_child = product_data["child"]
                product_discount = product_data["discount"]
                product_margen = product_data["margen"]
                product_iva = product_data["iva"]
                product_iva_value = product_data["iva_value"]
                product_status = product_data["status"]
                product_proveedor = product_data["proveedor"]
                product_step_unit = product_data["step_unit"]
            else:
                product_name = "Unknown"
                product_description = "Unknown"
                product_price_purchase = "N/A"
                product_category = "N/A"
                product_root = "N/A"
                product_child = "N/A"
                product_discount = "N/A"
                product_margen = "N/A"
                product_iva = "N/A"
                product_iva_value = "N/A"
                product_status = "N/A"
                product_proveedor = "N/A"
                product_step_unit = "N/A"

            csv_writer.writerow([
                order_id
                , order_number
                , customer_email
                , customer_phone
                , customer_document_number
                , customer_document_type
                , customer_name
                , delivery_date
                , status
                , created_at
                , updated_at
                , total
                , delivery_slot
                , payment_method
                , delivery_address
                , delivery_address_details
                , product_sku
                , product_name
                , product_description
                , product_quantity
                , product_price_sale
                , product_price_purchase
                , product_category
                , product_root
                , product_child
                , product_discount
                , product_margen
                , product_iva
                , product_iva_value
                , product_status
                , product_proveedor
                , product_step_unit                
            ])

    csv_file.seek(0)

    # Crear una respuesta y añadir los headers adecuados
    response = Response(csv_file.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'inline; filename=orders.csv'
    return response

def limpiar_valor(valor_str):
    """Limpia el valor, eliminando caracteres no numéricos y formatea como float."""
    if not valor_str:
        return 0.0
    # Reemplaza puntos, comas, símbolos y deja solo números y decimales
    valor_str = re.sub(r'[^\d,]', '', valor_str)
    valor_str = valor_str.replace(',', '.')
    try:
        return float(valor_str)
    except ValueError:
        return 0.0


def limpiar_valor(valor_str):
    if not valor_str:
        return 0.0
    valor_str = re.sub(r'[^\d,]', '', valor_str)
    valor_str = valor_str.replace(',', '.')
    try:
        return float(valor_str)
    except ValueError:
        return 0.0
@order_api.route('/order/order_file', methods=['POST'])
def update_order():
    print("Actualizando orden desde CSV")
    try:
        # Validación de archivo CSV
        if 'file' not in request.files or 'data' not in request.form:
            return jsonify({'message': 'Archivo CSV o datos faltantes'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'Archivo no seleccionado'}), 400

        # Parsear JSON con datos de la orden
        data = json.loads(request.form['data'])

        # Leer productos del CSV
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream, delimiter=';')

        productos = []
        total = 0.0

        for row in reader:
            sku = row.get('SKU').strip() if row.get('SKU') else ''
            quantity = limpiar_valor(row.get('CANTIDAD'))
            price = limpiar_valor(row.get('PRECIO'))

            if not sku:
                continue

            product = Product.find_by_sku(sku=sku)
            if not product:
                continue

            product_dict = product
            product_dict['quantity'] = quantity
            product_dict['price_sale'] = price
            productos.append(product_dict)
            total += quantity * price

        # Construir objeto Order
        order = Order(
            id=data.get('id'),
            order_number=data.get('order_number'),
            customer_email=data.get('email') or data.get('customer_email', ''),
            customer_phone=data.get('phoneNumber') or data.get('customer_phone', ''),
            customer_documentNumber=(data.get('documentNumber') or data.get('customer_documentNumber') or '').split('-')[0],
            customer_documentType=data.get('documentType') or data.get('customer_documentType', ''),
            customer_name=(data.get('customerName') or data.get('customer_name', '')).capitalize(),
            delivery_date=data.get('deliveryDate') or data.get('delivery_date', ''),
            status=data.get('status') or 'Creada',
            created_at=data.get('created_at', None),
            updated_at=data.get('updated_at', None),
            products=productos,
            total=total,
            deliverySlot=data.get('deliverySlot', '09:00-12:00'),
            paymentMethod=data.get('paymentMethod', 'Cash'),
            deliveryAddress=data.get('deliveryAddress', 'Default Address'),
            deliveryAddressDetails=data.get('deliveryAddressDetails', ''),
            deliveryCost=data.get('deliveryCost', 0.0),
            discount=data.get("discount", 0.0),
            alegra_id=data.get('alegra_id', '000'),
            open_hour=data.get('open_hour', ''),
            payment_date=data.get('payment_date', data.get('delivery_date')),
            driver_name=data.get('driver_name', ''),
            seller_name=data.get('seller_name', ''),
            source=data.get('source', 'Aplicación'),
            totalPayment=0.0,
            status_payment=data.get('status_payment', 'Pendiente')
        )
        print(order.to_json())
        # Validación mínima
        # if not order.customer_email or not order.delivery_date:
        #     return jsonify({'message': 'Campos requeridos faltantes'}), 400

        # # Verificar existencia
        # existing = Order.find_by_order_number(order.order_number)
        # if existing:
        #     order.updated()
        # else:
        #     order.save()
        #     send_order_email(order.order_number, order.customer_email, order.delivery_date, productos, total)

        return jsonify({'message': 'Orden creada exitosamente'}), 201

    except Exception as e:
        print(f"Error creando orden desde CSV: {e}")
        return jsonify({'message': str(e)}), 500
    
@order_api.route('/order/auto_order/<string:order_number>', methods=['GET'])
def update_order_from_csv(order_number, filename='clinica_daniel.csv'):
    try:
        # Construir ruta al archivo CSV desde el directorio de ejecución
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)

        if not os.path.exists(file_path):
            return jsonify({'message': f'CSV file not found: {filename}'}), 404

        # Buscar la orden existente
        order = Order.find_by_order_number(order_number=order_number)
        if not order:
            return jsonify({'message': f'Order {order_number} not found'}), 404

        # Leer CSV con separador ;
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')

            updated_products = []
            total = 0.0

            for row in reader:
                sku = row.get('SKU').strip() if row.get('SKU') else ''
                quantity = limpiar_valor(row.get('CANTIDAD'))
                price = limpiar_valor(row.get('PRECIO'))
                print(f"Processing SKU: {sku}, Quantity: {quantity}, Price: {price}")
                if not sku:
                    continue

                product = Product.find_by_sku(sku=sku)
                if not product:
                    continue

                product_dict = product
                product_dict['quantity'] = quantity
                product_dict['price_sale'] = price
                updated_products.append(product_dict)
                total += quantity * price
        order.products = updated_products
        order.updated()

        return jsonify({'message': 'Order updated successfully'}), 200

    except Exception as e:
        print(f"Error updating order from CSV: {e}")
        return jsonify({'message': str(e)}), 500