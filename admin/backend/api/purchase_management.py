from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
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
import certifi
import urllib.request
from datetime import datetime, timedelta
from ..models.purchase import Purchase
from collections import OrderedDict


purchase_api = Blueprint('purchase', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
orders_collection = db['orders']
purchase_collection = db['purchases']

def func_create_purchase(date,efectivo=0):
    date_object = datetime.strptime(date, "%Y-%m-%d")
    yesterday = date_object - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    date_str = date
    pipeline = [ 
        {
            "$match": {
                "delivery_date": date_str
            }
        },
        {
            "$unwind": "$products"
        },
        {
            "$lookup": {
                "from": "products",
                "localField": "products.sku",
                "foreignField": "sku",
                "as": "product_info"
            }
        },
        {
            "$unwind": "$product_info"
        },
        {
            "$addFields": {
                "is_child": {"$eq": ["$product_info.root", "0"]},
                "parent_sku": "$product_info.child",
                "adjusted_quantity": {
                    "$cond": {
                        "if": {"$eq": ["$product_info.root", "0"]},
                        "then": {"$multiply": ["$products.quantity", "$product_info.step_unit"]},
                        "else": "$products.quantity"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "sku": {"$cond": [{"$eq": ["$is_child", True]}, "$parent_sku", "$products.sku"]},
                    "client_name": "$customer_name"
                },
                "total_quantity_ordered": {"$sum": "$adjusted_quantity"}
            }
        },
        {
            "$group": {
                "_id": "$_id.sku",
                "total_quantity_ordered": {"$sum": "$total_quantity_ordered"},
                "clients": {
                    "$push": {
                        "client_name": "$_id.client_name",
                        "quantity": "$total_quantity_ordered"
                    }
                }
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
        "$lookup": {
            "from": "suppliers",
            "localField": "product_info.proveedor",
            "foreignField": "nickname",
            "as": "supplier_info"
        }
        },
        {
        "$unwind": {
            "path": "$supplier_info",
            "preserveNullAndEmptyArrays": True
        }
        },
        {
        "$addFields": {
            "supplier_info._id": {
            "$toString": "$supplier_info._id"
            }
        }
        },
        {
            "$lookup": {
                "from": "inventory",
                "let": {"sku": "$_id", "close_date": yesterday_str},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$close_date", "$$close_date"]},
                                    {"$in": ["$$sku", "$products.sku"]}
                                ]
                            }
                        }
                    },
                    {"$unwind": "$products"},
                    {
                        "$match": {
                            "$expr": {"$eq": ["$products.sku", "$$sku"]}
                        }
                    },
                    {
                        "$project": {
                            "quantity": "$products.quantity",
                            "_id": 0
                        }
                    }
                ],
                "as": "inventory_info"
            }
        },
        {
            "$addFields": {
                "inventory": {
                    "$ifNull": [{"$arrayElemAt": ["$inventory_info.quantity", 0]}, 0]
                }
            }
        },
        {
            "$addFields": {
                "total_quantity": {
                    "$ceil": {
                        "$add": [
                            "$total_quantity_ordered",
                            {"$ifNull": ["$forecast", 0]},
                            {"$multiply": ["$inventory", -1]}
                        ]
                    }
                }
            }
        },
        {
            "$match": {
                "total_quantity": {"$gt": 0}
            }
        },
        {
            "$project": {
                "_id": 0,
                "sku": "$_id",
                "name": "$product_info.name",
                "total_quantity_ordered": 1,
                "price_purchase": "$product_info.price_purchase",
                "forecast": {"$literal": 0},
                "inventory": 1,
                "proveedor": "$supplier_info",
                "type_transaction" : "$supplier_info.type_transaction",
                "total_quantity": 1,
                "category": "$product_info.category",
                "unit": "$product_info.unit",
                "status": "Creada",
                "link_document_support": "",
                "final_price_purchase": {"$literal": 0.0},
                "clients": 1
            }
        }
    ]

    products = list(orders_collection.aggregate(pipeline))
    if products:
        purchase_number = db['counters'].find_one_and_update(
            {"_id": "purchase_id"},
            {"$inc": {"sequence_value": 1}},
            upsert=True,
            return_document=True
        )["sequence_value"]
        purchase_document = {
            "date": date,
            "purchase_number": str(purchase_number),
            "efectivoEntreado": efectivo,
            "status": "Creada",
            "products": products,
            "comments" :""
        }
        purchase_collection.insert_one(purchase_document)
        return jsonify({"status": "success", "message": "Purchase document saved.", "purchase_number": purchase_number}), 201
    else:
        return jsonify({"status": "failure", "message": "No products found for the given date."}), 404
@purchase_api.route('/create/', methods=['POST'])
def create_purchase():
    data = request.json
    date = data.get("date")
    efectivo = data.get("efectivoEntreado")
    return func_create_purchase(date,efectivo)

@purchase_api.route('/purchases/', methods=['GET'])
def list_purchases():
    purchases = list(
        purchase_collection
        .find({}, {'_id': 0})
        .sort('date', -1)
        .limit(50)
    )
    return jsonify(purchases), 200

@purchase_api.route('/purchase/<string:purchaseNumber>', methods=['GET'])
def get_purchase(purchaseNumber):
    purchase = purchase_collection.find_one({"purchase_number" : purchaseNumber}, {'_id': 0})
    return jsonify(purchase), 200

@purchase_api.route('/purchase', methods=['PUT'])
def edit_purchase():
    data = request.get_json()
    result = purchase_collection.update_one(
        {"purchase_number": data.get('purchase_number')},
        {"$set": data}
    )
    if result.matched_count:
        return jsonify({"status": "success", "message": "Purchase updated successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Purchase not found."}), 404

@purchase_api.route('/purchase/<string:purchase_number>', methods=['DELETE'])
def delete_purchase(purchase_number):
    result = purchase_collection.delete_one({"purchase_number": purchase_number})
    if result.deleted_count:
        return jsonify({"status": "success", "message": "Purchase deleted successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Purchase not found."}), 404

@purchase_api.route('/update_price', methods=['POST'])
def update_price():
    data = request.json
    purchase_number = data.get("purchase_number")
    sku = data.get("sku")
    new_price = data.get("final_price_purchase")
    type_transaction = data.get("type_transaction", "Efectivo")
    new_proveedor = data.get("proveedor")
    forecast = data.get("forecast")
    total_quantity = data.get("total_quantity")
    purchase = purchase_collection.find_one({"purchase_number": purchase_number})
    status = data.get("status")
    if purchase:
        updated = False
        for product in purchase['products']:
            if product['sku'] == sku:
                # Actualiza el precio del producto
                product['final_price_purchase'] = new_price
                product['proveedor'] = new_proveedor
                product['type_transaction'] = type_transaction
                product['status'] = status
                product['forecast'] = forecast
                product['total_quantity'] = total_quantity
                updated = True
                break

        if updated:
            purchase_collection.update_one(
                {"purchase_number": purchase_number},
                {"$set": {"products": purchase['products']}}
            )
            return jsonify({"status": "success", "message": "Price updated successfully."}), 200
        else:
            return jsonify({"status": "failure", "message": "SKU not found."}), 404
    else:
        return jsonify({"status": "failure", "message": "Purchase not found."}), 404

@purchase_api.route('/purchase/report/<string:purchase_number>', methods=['GET'])
def get_report_purchase(purchase_number):
    pipeline = [
    {
        "$match": {
            "purchase_number": str(purchase_number)  # Asegurarse de que `purchase_number` es una cadena
        }
    },
    {
        "$unwind": "$products"  # Expandimos el array `products`
    },
    {
        "$match": {  # Filtramos productos con `total_quantity` mayor a 0
            "products.total_quantity": {"$gt": 0}
        }
    },
    {
        "$unwind": "$products.clients"  # Expandimos el array `clients` dentro de `products`
    },
    {
        "$group": {
            "_id": {
                "sku": "$products.sku",
                "name": "$products.name",
                "category": "$products.category",
                "unit": "$products.unit",
                "price_purchase": "$products.price_purchase",
                "total_quantity": "$products.total_quantity"  # Tomar directamente el valor de `total_quantity`
            },
            "date": {"$first": "$date"},  # Preservar la fecha original
            "clients_quantities": {
                "$push": {
                    "client_name": {
                        "$ifNull": ["$products.clients.client_name", "Sin Cliente"]
                    },
                    "quantity": {
                        "$ifNull": ["$products.clients.quantity", "0"]
                    }
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "sku": "$_id.sku",
            "name": "$_id.name",
            "total_quantity": "$_id.total_quantity",  # Directamente desde el producto
            "price_purchase": "$_id.price_purchase",
            "category": "$_id.category",
            "unit": "$_id.unit",
            "date": 1,
            "clients_quantities": {
                "$reduce": {
                    "input": "$clients_quantities",
                    "initialValue": "",
                    "in": {
                        "$concat": [
                            "$$value",
                            {
                                "$cond": {
                                    "if": {"$eq": ["$$value", ""]},
                                    "then": "",
                                    "else": " - "
                                }
                            },
                            {"$toString": "$$this.quantity"}
                        ]
                    }
                }
            }
        }
    },
    {
        "$sort": {
            "category": 1,
            "name": 1
        }
    }
]

    products = list(purchase_collection.aggregate(pipeline))
    purchase = Purchase.get_by_number(str(purchase_number))
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    image_url = 'https://buyfrescapp.com/images/banner1.png'
    context = urllib.request.ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(image_url, context=context) as response:
        image_data = response.read()
    image_stream = BytesIO(image_data)
    logo = Image(image_stream, width=200, height=70)
    centered_style = ParagraphStyle(
        name='Centered',
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.white,
        leading=50
    )

    pdf_content = []
    header_paragraph = Paragraph(
        '<font>Compras para el {}</font>'.format(str(products[0].get('date'))),
        centered_style
    )
    green_box = Table([[header_paragraph]], colWidths=[250], rowHeights=[70], style=[('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#97D700'))])
    content_table = Table([
        [logo, green_box]], colWidths=[200, 250])
    pdf_content.append(content_table)
    pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))
    
    table_width = 450
    product_data = [
        ['Nombre', 'Categoria', 'Cant. Total ', 'Pick','Precio Unit.','Precio Real'],  # Encabezado
    ]

    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    for product in products:
        name = product['name'] + " - ( " + product['sku'] + " )"
        clients_quantities = Paragraph(product['clients_quantities'], word_wrap_style)
        quantity_value = max(product.get('total_quantity', 0), 0)
        quantity = Paragraph(f"{quantity_value} {product.get('unit', '')}", word_wrap_style)
        price = locale.format_string('%.2f', round(product.get('price_purchase'),0), grouping=True)
        proveedor =  Paragraph('',word_wrap_style)
        name_paragraph = Paragraph(name, word_wrap_style)
        product_row = [name_paragraph, product.get('category'), quantity, clients_quantities, price,]
        product_data.append(product_row)
    
    total = locale.format_string('%.2f',sum(round(float(max(product.get('total_quantity', 0), 0)) * float(product['price_purchase']),0) for product in products), grouping=True)
    product_data.extend([['', '', '', '', '',''],
                         ['', '', '', 'Total', total,'']])
    
    col_widths = [
    0.4 * table_width,  # 40%
    0.15 * table_width,  # 20%
    0.20 * table_width,  # 20%
    0.10 * table_width, # 19%
    0.15 * table_width  # 19%
    ]
    product_table = Table(product_data, colWidths=col_widths)
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    comments = Paragraph(
        '<para bgColor="#FFD700" textColor="black" fontSize="12" leading="14" spaceAfter="12" align="center"><b>{}</b></para>'.format(str(purchase.comments)),
        centered_style
    )
    pdf_content.append(comments)
    pdf_content.append(product_table)
    pdf_content.append(PageBreak())

    pdf.build(pdf_content)
    buffer.seek(0)
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=compra_num_{}_{}.pdf'.format(purchase_number, str(products[0].get('date')))
    return response

@purchase_api.route('/purchase/detail/<string:purchase_number>', methods=['GET'])
def get_purchase_detail(purchase_number):
    purchase = purchase_collection.find_one({"purchase_number": purchase_number}, {'_id': 0})
    if not purchase:
        return jsonify({"status": "failure", "message": "Purchase not found."}), 404

    per_seller = OrderedDict()
    per_payment = OrderedDict()

    for product in purchase.get('products', []):
        proveedor_doc = product.get('proveedor', {})
        if not isinstance(proveedor_doc, dict):
            proveedor_doc = {}

        proveedor_nickname = proveedor_doc.get('nickname', 'Sin Proveedor')
        type_transaction = product.get('type_transaction', 'Efectivo')
        cantidad = product.get('total_quantity', 0)
        precio_estimado = product.get('price_purchase', 0)
        precio_real = product.get('final_price_purchase', 0)

        # ---------- Agrupar por nickname del proveedor ----------
        if proveedor_nickname not in per_seller:
            per_seller[proveedor_nickname] = {
                "cantidad_productos": 0,
                "valor_estimado": 0.0,
                "valor_real": 0.0
            }

        per_seller[proveedor_nickname]["cantidad_productos"] += cantidad
        per_seller[proveedor_nickname]["valor_estimado"] += cantidad * precio_estimado
        per_seller[proveedor_nickname]["valor_real"] += cantidad * precio_real

        # ---------- Agrupar por tipo de pago / estado ----------
        if type_transaction not in per_payment:
            per_payment[type_transaction] = {
                "cantidad_productos": 0,
                "valor_estimado": 0.0,
                "valor_real": 0.0
            }

        per_payment[type_transaction]["cantidad_productos"] += cantidad
        per_payment[type_transaction]["valor_estimado"] += cantidad * precio_estimado
        per_payment[type_transaction]["valor_real"] += cantidad * precio_real

    # Redondear y calcular totales al final
    def calcular_totales(grupo):
        total = {"cantidad_productos": 0, "valor_estimado": 0.0, "valor_real": 0.0}
        for key, val in grupo.items():
            val["valor_estimado"] = round(val["valor_estimado"], 2)
            val["valor_real"] = round(val["valor_real"], 2)
            total["cantidad_productos"] += val["cantidad_productos"]
            total["valor_estimado"] += val["valor_estimado"]
            total["valor_real"] += val["valor_real"]

        total["valor_estimado"] = round(total["valor_estimado"], 2)
        total["valor_real"] = round(total["valor_real"], 2)
        grupo["Total"] = total
        # Reordenar para poner TOTAL al final
        items = list(grupo.items())
        if items[-1][0] == "Total":
            items.append(items.pop())  # mover al final si no lo está
        return OrderedDict(items)

    per_seller = calcular_totales(per_seller)
    per_payment = calcular_totales(per_payment)

    return jsonify({
        "purchase_number": purchase.get("purchase_number"),
        "date": purchase.get("date"),
        "per_seller": per_seller,
        "per_payment": per_payment
    }), 200

@purchase_api.route('/purchase/<string:purchase_number>/remove-product/<string:sku>', methods=['DELETE'])
def remove_product_from_purchase(purchase_number, sku):
    result = purchase_collection.update_one(
        {"purchase_number": purchase_number},
        {"$pull": {"products": {"sku": sku}}}
    )

    if result.modified_count == 0:
        return jsonify({"status": "failure", "message": "Producto no encontrado o ya fue eliminado."}), 404

    return jsonify({"status": "success", "message": f"Producto con SKU {sku} eliminado de la compra {purchase_number}."}), 200
