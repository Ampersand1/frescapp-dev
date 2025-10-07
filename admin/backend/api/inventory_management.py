from models.inventory import Inventory
from models.product import Product
from models.purchase import Purchase
from models.order  import Order
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

inventory_api = Blueprint('inventory', __name__)

def func_create_inventory(close_date):
    products_data = Product.objects("active")
    fecha_ayer = (datetime.strptime(close_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    inventory_ayer = Inventory.get_by_date(fecha_ayer)
    inventory_hoy = Inventory.get_by_date(close_date)
    if inventory_hoy:
        return jsonify({"message": "Inventory already exists for today"}), 400
    compras_hoy = Purchase.get_by_date(close_date)
    ventas_hoy = Order.find_by_date(close_date,close_date)
    sku_mapping = {}
    for product in products_data:
        sku = product.get("sku")
        sku_mapping[sku] = {
            "root": product.get("child", sku),
            "step_unit": product.get("step_unit", 1)
        }
    def search_sku_root(sku_child):
        return sku_mapping.get(sku_child, {"root": sku_child, "step_unit": 1})
    products_data = Product.objects("active")
    filtered_products = [
        {
            "sku": product["sku"],
            "name": product["name"],
            "category": product["category"],
            "quantity": 0,  
            "quantity_auto": 0,
            "cost": product["price_purchase"]
        }
        for product in products_data if product.get("root") == "1" 
    ]
    item = Inventory(
        close_date=close_date,
        products=filtered_products
    ) 
    for product in filtered_products:
        sku = product["sku"]
        if inventory_ayer:
            producto_ayer = next((p for p in inventory_ayer.products if p["sku"] == sku), None)
            if producto_ayer:
                product["quantity_auto"] = round(producto_ayer["quantity"] or 0,1)
        if compras_hoy:
            compras_sku = [c for c in compras_hoy.products if c["sku"] == sku]
            for compra in compras_sku:
                product["quantity_auto"] += round(compra.get("total_quantity",0),1)
        if ventas_hoy:
            ventas_hoy = Order.find_by_date(close_date,close_date)
            for orden in ventas_hoy:
                for productOrder in orden.get("products", []):
                    sku_child = productOrder.get("sku")
                    temp = search_sku_root(sku_child)
                    sku_root = temp.get("root")
                    step_unit = temp.get("step_unit", 1)
                    if str(product.get("sku")) == str(sku_root):
                        quantity_sold = productOrder.get("quantity", 0)
                        product["quantity_auto"] -= round((quantity_sold * step_unit),1)
        product["quantity_auto"] = max(0, product["quantity_auto"])
        #product["quantity"] = max(0, product["quantity_auto"])
    item.save()
    return jsonify({"message": "Inventory item added successfully", "id": item.id}), 201

@inventory_api.route('/inventories', methods=['GET'])
def get_inventories():
    items = Inventory.get_last_10()
    return jsonify([{
        "id": str(item["_id"]),
        "close_date": item.get("close_date"),
        "products": item.get("products", [])
    } for item in items])

@inventory_api.route('/inventory/<inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    item = Inventory.get_by_id(inventory_id)
    if not item:
        return jsonify({"message": "Inventory not found"}), 404

    # Construir la respuesta con los datos del inventario
    response = {
        "id": str(item.id),
        "close_date": item.close_date,
        "products": [
            {
                "sku": product.get("sku"),
                "name": product.get("name"),
                "category": product.get("category"),
                "quantity": product.get("quantity", 0),
                "quantity_auto": product.get("quantity_auto", 0),
                "cost": product.get("cost", 0)
            }
            for product in item.products
        ]
    }
    return jsonify(response), 200

@inventory_api.route('/create/<close_date>', methods=['GET'])
def create_inventory(close_date):
    return func_create_inventory(close_date)

@inventory_api.route('/inventory/<inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    data = request.json
    item = Inventory.get_by_id(inventory_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    item.close_date = data.get('close_date', item.close_date)
    item.products = data.get('products', item.products)
    item.save()
    return jsonify({"message": "Inventory updated successfully"})

@inventory_api.route('/inventory/<inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    deleted_count = Inventory.delete_by_id(inventory_id)
    if deleted_count:
        return jsonify({"message": "Inventory deleted successfully"})
    return jsonify({"error": "Item not found"}), 404

