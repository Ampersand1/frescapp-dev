import 'package:flutter/material.dart';
//import 'package:frescapp/screens/login_screen.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart'; // Importa la pantalla de inicio
import 'package:frescapp/routes.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:frescapp/api_routes.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
    SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Frescapp',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0x0097d700)),
        useMaterial3: true,
      ),

      // Utiliza una función asincrónica para determinar qué pantalla mostrar
      home: FutureBuilder<bool>(
        future: _checkTokenValidity(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            // Muestra una pantalla de carga mientras se verifica el token
             return Scaffold(
            body: Center(
              child: Image.asset(
                'images/icon-app.png', // Cambia a la ruta de tu logo
                width: 150,              // Ajusta el tamaño según prefieras
                height: 150,
              ),
            ),
          );
          } else {
            return const HomeScreen();
          }
        },
      ),
      onGenerateRoute: Routes.generateRoute,
    );
  }

  // Función para verificar la validez del token almacenado en las preferencias compartidas
  Future<bool> _checkTokenValidity() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    // Verifica si hay un token y devuelve true si es válido, de lo contrario, devuelve false
    if (token != null) {
      final response = await http.post(
        Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/check_token'), // Endpoint para verificar el token
        
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer $token'
        },
      );
      return response.statusCode == 200;
    } else {
      return false;
    }
  }
}
