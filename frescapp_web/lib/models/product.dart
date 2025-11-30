class Product {
  final String? id;
  final String? name;
  final String? root;
  final String? child;
  final String? unit;
  final String? category;
  final String? sku;

  final double? priceSale;
  final double? pricePurchase;
  final double? discount;
  final double? margen;
  final bool? iva;
  final double? ivaValue;

  final String? description;
  final String? image;
  final String? status;
  final String? proveedor;

  final double? stepUnit;
  final double? rateRoot;

  /// CANTIDAD MODIFICABLE
  double? quantity;

  // Campos para descuentos
  final double? finalPrice;
  final bool hasDiscount;
  final String? discountType;
  final double? discountValue;
  final double? savingsPct;

  Product({
    this.id,
    this.name,
    this.root,
    this.child,
    this.unit,
    this.category,
    this.sku,
    this.priceSale,
    this.pricePurchase,
    this.discount,
    this.margen,
    this.iva,
    this.ivaValue,
    this.description,
    this.image,
    this.status,
    this.proveedor,
    this.stepUnit,
    this.rateRoot,
    this.quantity,
    this.finalPrice,
    this.hasDiscount = false,
    this.discountType,
    this.discountValue,
    this.savingsPct,
  });

  /// Conversión robusta a double
  static double _toDouble(dynamic v) {
    if (v == null) return 0.0;
    if (v is double) return v;
    if (v is int) return v.toDouble();
    if (v is num) return v.toDouble();
    if (v is String) return double.tryParse(v) ?? 0.0;
    return 0.0;
  }

  /// Conversión segura de IVA
  static bool? _toBool(dynamic v) {
    if (v == null) return null;
    if (v is bool) return v;
    if (v is int) return v == 1;
    if (v is String) return v.toLowerCase() == "true";
    return null;
  }

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json["id"] as String?,
      name: json["name"],
      root: json["root"],
      child: json["child"],
      unit: json["unit"],
      category: json["category"],
      sku: json["sku"],

      priceSale: _toDouble(json["price_sale"]),
      pricePurchase: _toDouble(json["price_purchase"]),
      discount: _toDouble(json["discount"]),
      margen: _toDouble(json["margen"]),
      iva: _toBool(json["iva"]),
      ivaValue: _toDouble(json["iva_value"]),

      description: json["description"],
      image: json["image"],
      status: json["status"],
      proveedor: json["proveedor"],

      stepUnit: _toDouble(json["step_unit"]),
      rateRoot: _toDouble(json["rate_root"]),
      quantity: _toDouble(json["quantity"]),

      // Campos descuento
      finalPrice: _toDouble(json["final_price"] ?? json["price_sale"]),
      hasDiscount: json["has_discount"] ?? false,
      discountType: json["discount_type"],
      discountValue: _toDouble(json["discount_value"]),
      savingsPct: _toDouble(json["savings_pct"]),
    );
  }

  /// Necesario para serializar orders
  Map<String, dynamic> toJson() {
    return {
      "id": id,
      "name": name,
      "root": root,
      "child": child,
      "unit": unit,
      "category": category,
      "sku": sku,

      "price_sale": priceSale,
      "price_purchase": pricePurchase,
      "discount": discount,
      "margen": margen,
      "iva": iva,
      "iva_value": ivaValue,

      "description": description,
      "image": image,
      "status": status,
      "proveedor": proveedor,

      "step_unit": stepUnit,
      "rate_root": rateRoot,

      "quantity": quantity,

      // descuento
      "final_price": finalPrice,
      "has_discount": hasDiscount,
      "discount_type": discountType,
      "discount_value": discountValue,
      "savings_pct": savingsPct,
    };
  }
}
