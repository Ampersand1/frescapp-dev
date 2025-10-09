import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/models/product.dart';

class ProductService {

  Future<List<Product>> getProducts(customerEmail) async {
    // ignore: prefer_interpolation_to_compose_strings
    final response = await http.get(Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.products}/products_customer/$customerEmail'));
    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = jsonDecode(response.body);
      List<Product> products = jsonResponse.map((data) => Product.fromJson(data)).toList();
      return products;
    } else {
      throw Exception('Failed to load products');
    }
  }
}
