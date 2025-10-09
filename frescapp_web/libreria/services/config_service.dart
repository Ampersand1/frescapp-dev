import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frescapp/api_routes.dart';

class ConfigService {
  final http.Client httpClient;

  ConfigService(this.httpClient);

  Future<Map<String, dynamic>> getConfigData() async {
    final response = await httpClient.get(Uri.parse('${ApiRoutes.baseUrl}/config/configOrder'));
    if (response.statusCode == 200) {
      // Decodifica la respuesta JSON
      final dynamic responseData = jsonDecode(response.body);
      if (responseData is Map<String, dynamic>) {
        return responseData;
      } else {
        throw const FormatException('Invalid data format');
      }
    } else {
      throw http.ClientException('Failed to load config data');
    }
  }
}
