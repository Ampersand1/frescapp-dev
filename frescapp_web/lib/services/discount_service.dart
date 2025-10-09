import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frescapp/api_routes.dart';

class DiscountService {
  Future<double> validateCode(String discountCode, String customerEmail) async {
    final response = await http.post(
      Uri.parse('${ApiRoutes.baseUrl}/discount/discount/validate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'discount_code': discountCode, 'customer_email': customerEmail}),
    );

    if (response.statusCode == 200) {
      var data = jsonDecode(response.body);
      if (data['value'] != null  && data['value'] > 0.0) {
        return data['value']*1.0 as double;
      } else {
        return 0.0;
      }
    } else {
      return 0.0;
    }
  }
}
