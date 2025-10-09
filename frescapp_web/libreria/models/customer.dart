class Customer {
  final String id;
  final String phone;
  final String name;
  final String document;
  final String documentType;
  final String address;
  final String restaurantName;
  final String email;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String category;
  final List<String> listProducts;

  Customer({
    required this.id,
    required this.phone,
    required this.name,
    required this.document,
    required this.documentType,
    required this.address,
    required this.restaurantName,
    required this.email,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    required this.category,
    required this.listProducts,
  });

  factory Customer.fromJson(Map<String, dynamic> json) {
    return Customer(
      id: json['_id']['\$oid'],
      phone: json['phone'],
      name: json['name'],
      document: json['document'],
      documentType: json['document_type'],
      address: json['address'],
      restaurantName: json['restaurant_name'],
      email: json['email'],
      status: json['status'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      category: json['category'],
      listProducts : json['list_products']
    );
  }

  Map<String, dynamic> toJson() {
    return {
      '_id': {'\$oid': id},
      'phone': phone,
      'name': name,
      'document': document,
      'document_type': documentType,
      'address': address,
      'restaurant_name': restaurantName,
      'email': email,
      'status': status,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'category': category,
      'list_products' : listProducts
    };
  }
}
