import 'package:frescapp/models/product.dart';

class Order {
  String? id;
  String? orderNumber;
  String? customerEmail;
  String? customerPhone;
  String? customerDocumentNumber;
  String? customerDocumentType;
  String? customerName;
  String? deliveryDate;
  String? status;
  String? createdAt;
  String? updatedAt;
  List<Product>? products;
  double? total;
  String? deliverySlot;
  String? paymentMethod;
  String? deliveryAddress;
  String? deliveryAddressDetails;
  double? deliveryCost;
  double? discount;

  Order({
    this.id,
    this.orderNumber,
    this.customerEmail,
    this.customerPhone,
    this.customerDocumentNumber,
    this.customerDocumentType,
    this.customerName,
    this.deliveryDate,
    this.status,
    this.createdAt,
    this.updatedAt,
    this.products,
    this.total,
    this.deliverySlot,
    this.paymentMethod,
    this.deliveryAddress,
    this.deliveryAddressDetails,
    this.deliveryCost,
    this.discount,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] as String?,
      orderNumber: json['order_number'] as String?,
      customerEmail: json['customer_email'] as String?,
      customerPhone: json['customer_phone'] as String?,
      customerDocumentNumber: json['customer_documentNumber'] as String?,
      customerDocumentType: json['customer_documentType'] as String?,
      customerName: json['customer_name'] as String?,
      deliveryDate: json['delivery_date'] as String?,
      status: json['status'] as String?,
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
      products: (json['products'] as List<dynamic>?)
          ?.map((productJson) => Product.fromJson(productJson))
          .toList(),
      total: (json['total'] as num?)?.toDouble(),
      deliverySlot: json['deliverySlot'] as String?,
      paymentMethod: json['paymentMethod'] as String?,
      deliveryAddress: json['deliveryAddress'] as String?,
      deliveryAddressDetails: json['deliveryAddressDetails'] as String?,
      deliveryCost: (json['deliveryCost'] as num?)?.toDouble(),
      discount: (json['discount'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'order_number': orderNumber,
      'customer_email': customerEmail,
      'customer_phone': customerPhone,
      'customer_documentNumber': customerDocumentNumber,
      'customer_documentType': customerDocumentType,
      'customer_name': customerName,
      'delivery_date': deliveryDate,
      'status': status,
      'created_at': createdAt,
      'updated_at': updatedAt,
      'products': products?.map((product) => product.toJson()).toList(),
      'total': total,
      'deliverySlot': deliverySlot,
      'paymentMethod': paymentMethod,
      'deliveryAddress': deliveryAddress,
      'deliveryAddressDetails': deliveryAddressDetails,
      'deliveryCost': deliveryCost,
      'discount': discount,
    };
  }

  /// Getter para calcular total en el frontend (opcional)
  double get calculatedTotal {
    if (products == null) return 0.0;
    return products!
        .map((p) => (p.priceSale ?? 0) * (p.quantity ?? 1))
        .fold(0.0, (prev, elem) => prev + elem);
  }
}
