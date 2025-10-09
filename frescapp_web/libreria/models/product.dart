class Product {
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
  double? quantity; 

  Product({
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
    this.quantity, // Asignación del nuevo atributo quantity
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      name: json['name'] as String?,
      root: json['root'] as String?,
      child: json['child'] as String?,
      unit: json['unit'] as String?,
      category: json['category'] as String?,
      sku: json['sku'] as String?,
      priceSale: (json['price_sale'] as num?)?.toDouble(),
      pricePurchase: (json['price_purchase'] as num?)?.toDouble(),
      discount: (json['discount'] as num?)?.toDouble(),
      margen: (json['margen'] as num?)?.toDouble(),
      iva: json['iva'] as bool?,
      ivaValue: (json['iva_value'] as num?)?.toDouble(),
      description: json['description'] as String?,
      image: json['image'] as String?,
      status: json['status'] as String?,
      proveedor: json['proveedor'] as String?,
      stepUnit: json['step_unit'] as double?,
      rateRoot: json['rate_root'] as double?,
      quantity: (json['quantity'] as double?),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'root': root,
      'child': child,
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
      'proveedor': proveedor,
      'step_unit': stepUnit,
      'rate_root': rateRoot,
      'quantity': quantity,
    };
  }
}
