import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frescapp/models/product.dart';
import 'package:frescapp/api_routes.dart';

class ProductService {
  Future<List<Product>> getProducts(String userEmail) async {
    final safeEmail = (userEmail.isEmpty) ? 'undefined' : userEmail;
    final response = await http.get(
      Uri.parse('${ApiRoutes.baseUrl}/products_customer/$safeEmail'),
    );

    if (response.statusCode == 200) {
      List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Product.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load products');
    }
  }

  Future<List<Product>> getDiscountedProducts({String search = ''}) async {
    final response = await http.get(
      Uri.parse('${ApiRoutes.baseUrl}/products/discounts?search=$search'),
    );

    if (response.statusCode == 200) {
      List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Product.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load discounted products');
    }
  }
}
