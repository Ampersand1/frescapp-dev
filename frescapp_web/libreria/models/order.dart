import 'package:frescapp/models/product.dart';

class Order {
  late String? id;
  late String? orderNumber;
  late String? customerEmail;
  late String? customerPhone;
  late String? customerDocumentNumber;
  late String? customerDocumentType;
  late String? customerName;
  late String? deliveryDate;
  late String? status;
  late String? createdAt;
  late String? updatedAt;
  late List<Product>? products;
  late double? total;
  late String? deliverySlot;
  late String? paymentMethod;
  late String? deliveryAddress;
  late String? deliveryAddressDetails;
  late double? deliveryCost; 
  late double? discount;
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
    this.discount
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
      deliveryCost : json['deliveryCost'] as double?,
      discount : 0.0 as double?

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
      'discount' : discount
    };
  }
}
