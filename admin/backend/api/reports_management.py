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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from io import BytesIO
from pymongo import MongoClient
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak
import locale
from models.customer import Customer
from models.product import Product
from models.inventory import Inventory
from datetime import datetime, timedelta

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
report_api = Blueprint('report', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
orders_collection = db['orders']  
products_collection = db['orders']  
@report_api.route('/picking/<string:startDate>/<string:endDate>', methods=['GET'])
def get_picking(startDate, endDate): 
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
    orders = orders_collection.find({"delivery_date": {"$gte": startDate, "$lte": endDate }})

    for order in orders:
        if not order:
            return jsonify({'message': 'Order not found'}), 404        

        word_wrap_style = styles["Normal"]
        word_wrap_style.wordWrap = 'CJK'

        # Datos de la orden
        order_data = [
            [logo, 'Remisión #', order['order_number'], 'Fecha', order['delivery_date']],
            ['', 'Nombre', Paragraph(order['customer_name'], word_wrap_style), 'Teléfono del Cliente', Paragraph(order['customer_phone'], word_wrap_style)],
            ['', 'Método de pago', Paragraph(order['paymentMethod'], word_wrap_style), 'Horario de entrega', Paragraph(order['deliverySlot'] + ' (' + order['open_hour'] + ')', word_wrap_style)],
            ['Dirección de entrega', Paragraph(order['deliveryAddress'], word_wrap_style),  'Detalle de entrega', Paragraph(order['deliveryAddressDetails'], word_wrap_style),'']
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

        # Aplicar estilos de WordWrap
        word_wrap_style = styles["Normal"]
        word_wrap_style.wordWrap = 'CJK'

        product_data = [
            ['SKU', 'Nombre', 'Cantidad', 'Precio Unitario', 'Total'],  # Encabezado
        ]
        for product in sorted(list(order['products']), key=lambda x: x['name']):
            sku = product['sku']
            name = product['name']
            quantity = product['quantity']
            price_sale = locale.format_string('%.0f', round(product.get('price_sale'),0), grouping=True)
            total = locale.format_string('%.0f', round(float(product.get('price_sale')) * float(quantity),0), grouping=True)
            name_paragraph = Paragraph(name, word_wrap_style)
            product_row = [sku, name_paragraph, str(quantity)  + "  " + str(product.get('unit', '')), price_sale, total]
            product_data.append(product_row)

        subtotal = sum(round(float(product['quantity']) * float(product['price_sale']),0) for product in list(order['products']))
        descuentos = float(order.get('discount', 0))
        total = subtotal - descuentos
        subtotal_formatted = locale.format_string('%.2f', subtotal, grouping=True)
        descuentos_formatted = locale.format_string('%.2f', descuentos, grouping=True)
        total_formatted = locale.format_string('%.2f', total, grouping=True)
        image_path_payment = 'https://buyfrescapp.com/images/medio_pago.png'  # URL o ruta local de la imagen del medio de pago
        payment_image = Image(image_path_payment, width=290, height=80)  # Ajustar tamaño de la imagen
        product_data.extend([[payment_image,'','','',''],
            ['', '', '', 'Subtotal', subtotal_formatted],
            ['', '', '', 'Descuentos', descuentos_formatted],
            ['', '', '', 'Total', total_formatted]
        ])
        product_table = Table(product_data, colWidths=[120,200,80,80,80])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),  # Color de fondo del encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Añadir bordes internos a las celdas
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, len(list(order['products']))+1), (2, len(list(order['products']))+4))
        ]))
        pdf_content.append(product_table)
        pdf_content.append(PageBreak())

    pdf.build(pdf_content)
    buffer.seek(0)
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=remisiones_{}_{}.pdf'.format(startDate,endDate)
    return response

@report_api.route('/compras/<string:date>/<string:supplier>', methods=['GET'])
def get_compras(date,supplier):
    pipeline = [
        {
            "$match": {
                "delivery_date": date
            }
        },
        {
            "$unwind": "$products"
        },
        {
            "$group": {
                "_id": "$products.sku",
                "total_quantity_ordered": {"$sum": "$products.quantity"}
            }
        },
        {
            "$lookup": {
                "from": "products",
                "localField": "_id",
                "foreignField": "sku",
                "as": "product_info"
            }
        },
        {
            "$unwind": "$product_info"
        },
        {
            "$project": {
                "_id": 0,
                "sku": "$_id",
                "name": "$product_info.name",
                "total_quantity_ordered": 1,
                "price_purchase": "$product_info.price_purchase",
                "proveedor": "$product_info.proveedor",
                "category": "$product_info.category",
                "unit": "$product_info.unit"
            }
        }
    ]
    if supplier != 'Todos':
        pipeline.append({
            "$match": {
                "proveedor": supplier
            }
        })
    pipeline.append({
        "$sort": {
            "category": 1 ,
            "name":1
        }
    })
    products = list(orders_collection.aggregate(pipeline))
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    image_path = 'https://app.buyfrescapp.com:5000/api/shared/banner1.png'
    logo = Image(image_path, width=200, height=70)
    centered_style = ParagraphStyle(
            name='Centered',
            fontSize=16,  # Tamaño de la letra aumentado a 16
            alignment=TA_CENTER,  # Centrado horizontal
            textColor=colors.white,  # Color del texto blanco
            leading=50  # Espaciado entre líneas para centrar verticalmente
        )
    pdf_content = []
    compras_paragraph = Paragraph('<font>Compras para el {}</font>'.format(date), centered_style)
    green_box = Table([[compras_paragraph]], colWidths=[250], rowHeights=[70], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#97D700'))])
    content_table = Table([
    [logo, green_box]], colWidths=[200, 250])
    pdf_content.append(content_table)
    pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))
    table_width = 500
    product_data = [
        [ 'Nombre', 'Categoria', 'Cantidad', 'Precio Unitario', 'Proveedor','Proveedor Final', 'Precio Final'],  # Encabezado
    ]
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    for product in products:
        sku = product['sku']
        name = product['name'] + " - ( "+sku+" )"
        quantity = Paragraph(str(product.get('total_quantity_ordered')) + "  " + str(product.get('unit')),word_wrap_style)
        price = locale.format_string('%.2f', round(product.get('price_purchase'),0), grouping=True)
        proveedor = product['proveedor']
        name_paragraph = Paragraph(name, word_wrap_style)
        product_row = [ name_paragraph, product.get('category'), quantity, price, proveedor]
        product_data.append(product_row)
    total = locale.format_string('%.2f',sum(round(float(product['total_quantity_ordered']) * float(product['price_purchase']),0) for product in products), grouping=True)
    product_data.extend([['','','','',''],
            ['', '', 'Total', total, '']
        ])
    col_widths = [(2 / 8) * table_width] + [(1 / 8) * table_width] * 4
    product_table = Table(product_data, colWidths=col_widths)
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),  # Color de fondo del encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Añadir bordes internos a las celdas
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black)  # Añadir borde alrededor de la tabla
    ]))
    pdf_content.append(product_table)
    pdf_content.append(PageBreak())

    pdf.build(pdf_content)
    buffer.seek(0)
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=ordenes_{}.pdf'.format(date)
    return response

@report_api.route('/picking_summary/<string:forecastDate>', methods=['GET'])
def get_picking_summary(forecastDate):
    from datetime import datetime, timedelta

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=28.35, rightMargin=28.35,
                            topMargin=28.35, bottomMargin=28.35)
    styles = getSampleStyleSheet()
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'
    pdf_content = []

    inventory_date = (datetime.strptime(forecastDate, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

    orders = list(orders_collection.find({"delivery_date": forecastDate}))
    inventory = {i['sku']: i for i in Inventory.get_by_date(inventory_date).products}

    productos = {}
    for order in orders:
        for p in order['products']:
            sku = p['sku']
            if sku not in productos:
                productos[sku] = {
                    'name': p['name'],
                    'unit': p.get('unit', ''),
                    'cantidades': []
                }
            productos[sku]['cantidades'].append((f"{order['order_number']} - {order['customer_name']}", p['quantity']))

    pronostico = {}
    reactivo = {}

    for sku, p in sorted(productos.items(), key=lambda x: x[1]['name'].lower()):
        total_qty = sum(q for _, q in p['cantidades'])
        inv_qty = inventory.get(sku, {}).get('quantity', 0)
        destino = pronostico if inv_qty >= total_qty else reactivo

        destino.setdefault(p['name'], {'unit': p['unit'], 'rows': [], 'total': 0})
        destino[p['name']]['total'] += total_qty
        for cliente, qty in p['cantidades']:
            destino[p['name']]['rows'].append((cliente, qty))

    def build_table(titulo, data_dict):
        tabla = [[titulo]]
        tabla.append(['Producto (Total)', 'Cliente', 'Cantidad'])
        span_ranges = []

        for nombre, info in data_dict.items():
            total = info['total']
            unit = info['unit']
            filas = info['rows']
            producto_label = Paragraph(f"<b>{nombre} (Total: {total} {unit})</b>", word_wrap_style)
            start_row = len(tabla)

            for i, (cliente, qty) in enumerate(filas):
                tabla.append([
                    producto_label if i == 0 else '',  # solo en la primera fila
                    Paragraph(cliente, word_wrap_style),
                    Paragraph(f"{qty} {unit}", word_wrap_style)
                ])
            end_row = len(tabla) - 1
            span_ranges.append((0, start_row, 0, end_row))

        estilos = [
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#97D700')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('SPAN', (0, 0), (-1, 0)),  # título tabla
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 1), (-1, -1), 0.5, colors.black),
        ]
        for r in span_ranges:
            estilos.append(('SPAN', r[0:2], r[2:4]))
            estilos.append(('VALIGN', r[0:2], r[2:4], 'MIDDLE'))

        t = Table(tabla, colWidths=[230, 200, 120])
        t.setStyle(TableStyle(estilos))
        return t

    if pronostico:
        pdf_content.append(build_table("PRONÓSTICO", pronostico))
        pdf_content.append(Spacer(1, 20))
    if reactivo:
        pdf_content.append(build_table("REACTIVO", reactivo))

    pdf.build(pdf_content)
    buffer.seek(0)
    return Response(buffer, mimetype='application/pdf',
                    headers={'Content-Disposition': f'inline; filename=picking_summary_{forecastDate}.pdf'})
