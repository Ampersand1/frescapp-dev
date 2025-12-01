class Product {
  String? id;
  String? name;
  String? unit;
  String? category;
  String? sku;
  double? priceSale;
  double? pricePurchase;
  double? discount;
  double? margen;
  bool? iva;
  double? ivaValue;
  String? description;
  String? image;
  String? status;
  int? quantity;
  String? root;
  String? child;
  String? proveedor;
  double? stepUnit;
  double? rateRoot;

  // NUEVOS CAMPOS para descuentos
  double? finalPrice;
  bool hasDiscount = false;
  String? discountType;
  double? discountValue;
  double? savingsPct;

  Product({
    this.id,
    this.name,
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
    this.quantity,
    this.root,
    this.child,
    this.proveedor,
    this.stepUnit,
    this.rateRoot,
    this.finalPrice,
    this.hasDiscount = false,
    this.discountType,
    this.discountValue,
    this.savingsPct,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String?,
      name: json['name'] as String?,
      unit: json['unit'] as String?,
      category: json['category'] as String?,
      sku: json['sku'] as String?,
      priceSale: (json['price_sale'] ?? 0).toDouble(),
      pricePurchase: (json['price_purchase'] ?? 0).toDouble(),
      discount: (json['discount'] ?? 0).toDouble(),
      margen: (json['margen'] ?? 0).toDouble(),
      iva: json['iva'] ?? false,
      ivaValue: (json['iva_value'] ?? 0).toDouble(),
      description: json['description'] as String?,
      image: json['image'] as String?,
      status: json['status'] as String?,
      quantity: json['quantity'] ?? 0,
      root: json['root'] as String?,
      child: json['child'] as String?,
      proveedor: json['proveedor'] as String?,
      stepUnit: (json['step_unit'] ?? 1).toDouble(),
      rateRoot: (json['rate_root'] ?? 0).toDouble(),
      // CAMPOS DE DESCUENTO
      finalPrice: (json['finalPrice'] ?? json['price_sale'] ?? 0).toDouble(),
      hasDiscount: json['hasDiscount'] ?? false,
      discountType: json['discountType'] as String?,
      discountValue: (json['discountValue'] ?? 0).toDouble(),
      savingsPct: (json['savingsPct'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'unit': unit,
      'category': category,
      'sku': sku,
      'price_sale': priceSale,
      'price_purchase': pricePurchase,
      'discount': discount,
      'margen': margen,
      'iva': iva,
      'iva_value': ivaValue,
      'description': description,
      'image': image,
      'status': status,
      'quantity': quantity,
      'root': root,
      'child': child,
      'proveedor': proveedor,
      'step_unit': stepUnit,
      'rate_root': rateRoot,
      // CAMPOS DE DESCUENTO
      'finalPrice': finalPrice,
      'hasDiscount': hasDiscount,
      'discountType': discountType,
      'discountValue': discountValue,
      'savingsPct': savingsPct,
    };
  }

  // -------------------------
  // Método para actualizar descuento directamente desde el backend
  // -------------------------
  void updateDiscount({
    double? finalPrice,
    bool? hasDiscount,
    String? discountType,
    double? discountValue,
    double? savingsPct,
  }) {
    this.finalPrice = finalPrice ?? this.finalPrice;
    this.hasDiscount = hasDiscount ?? this.hasDiscount;
    this.discountType = discountType ?? this.discountType;
    this.discountValue = discountValue ?? this.discountValue;
    this.savingsPct = savingsPct ?? this.savingsPct;
  }
}
