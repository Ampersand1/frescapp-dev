import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/models/product.dart';

class ProductService {
  /// Obtiene productos del cliente y aplica descuentos
  Future<List<Product>> getProducts(String? customerEmail) async {
    final safeEmail = (customerEmail == null || customerEmail.isEmpty) ? 'undefined' : customerEmail;

    // 1) Traer productos
    final response = await http.get(
      Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.products}/products_customer/$safeEmail'),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to load products');
    }

    List<Product> products = (jsonDecode(response.body) as List)
        .map((data) => Product.fromJson(data))
        .toList();

    // 2) Traer productos con descuento
    final discountResponse = await http.get(
      Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.products}/products/discounts'),
    );

    if (discountResponse.statusCode == 200) {
      List<dynamic> discountJson = jsonDecode(discountResponse.body);
      Map<String, dynamic> discountMap = {
        for (var d in discountJson) d['sku']: d
      };

      // 3) Aplicar descuentos a los productos
      for (var p in products) {
        if (discountMap.containsKey(p.sku)) {
          var d = discountMap[p.sku];
          p.updateDiscount(
            finalPrice: (d['price_final'] ?? p.priceSale)?.toDouble(),
            hasDiscount: true,
            discountType: d['discount_type'],
            discountValue: (d['value'] ?? 0).toDouble(),
            savingsPct: (d['discount_percentage'] ?? 0).toDouble(),
          );
        } else {
          p.updateDiscount(
            finalPrice: p.priceSale,
            hasDiscount: false,
            discountType: null,
            discountValue: 0.0,
            savingsPct: 0.0,
          );
        }
      }
    }

    return products;
  }
}
