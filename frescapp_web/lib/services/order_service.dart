import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/models/order.dart';

class OrderService {
  Future<List<Order>> getOrders(String email) async {
    final response = await http.get(Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.orders}/orders_customer/$email'));

    if (response.statusCode == 200) {
      String responseBody = response.body;
      List<dynamic> orderDataList = jsonDecode(responseBody);
      List<Order> orders = orderDataList.map((data) {
        return Order.fromJson(data);
      }).toList();
      return orders;
    } else {
      throw Exception('Failed to load orders');
    }
  }

  Future<void> createOrder(String orderNumber, Order order) async {
    final url = Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.orders}/order/$orderNumber');
    final headers = {'Content-Type': 'application/json'};
    final body = jsonEncode(order.toJson());

    final response = await http.post(url, headers: headers, body: body);

    if (response.statusCode != 200) {
      throw Exception('Failed to create order');
    }
  }
}
