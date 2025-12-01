// lib/services/coupon_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class CouponService {
  final String baseUrl;
  final http.Client client;

  CouponService({required this.baseUrl, http.Client? client})
      : client = client ?? http.Client();

  /// Valida un código contra el backend.
  /// Expected response:
  /// 200 OK -> { valid: true, coupon: { ... } }
  /// 400/404 -> { valid: false, message: "..." }
  Future<Map<String, dynamic>> validateCoupon(String code, double cartTotal, String userId) async {
    final url = Uri.parse('$baseUrl/api/coupons/validate');
    final body = jsonEncode({'code': code, 'cartTotal': cartTotal, 'userId': userId});
    final resp = await client.post(url, body: body, headers: {'Content-Type': 'application/json'});
    if (resp.statusCode == 200) {
      final jsonResp = jsonDecode(resp.body) as Map<String, dynamic>;
      return jsonResp; // { valid: true, coupon: {...} }
    } else {
      final jsonResp = jsonDecode(resp.body) as Map<String, dynamic>? ?? {};
      return {'valid': false, 'message': jsonResp['message'] ?? 'Error de validación'};
    }
  }
}
