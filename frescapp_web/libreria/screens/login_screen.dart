import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/forgot_password_screen.dart';

class LoginScreen extends StatelessWidget {
  LoginScreen({super.key});

  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  Future<void> _saveUserInfo(dynamic user) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    prefs.setString('user_id', user['user_data']['_id']);
    prefs.setString('user_phone', user['user_data']['phone']);
    prefs.setString('user_name', user['user_data']['name']);
    prefs.setString('user_document', user['user_data']['document']);
    prefs.setString('user_document_type', user['user_data']['document_type']);
    prefs.setString('user_address', user['user_data']['address']);
    prefs.setString('user_restaurant_name', user['user_data']['restaurant_name']);
    prefs.setString('user_email', user['user_data']['email']);
    prefs.setString('user_status', user['user_data']['status']);
    prefs.setString('user_created_at', user['user_data']['created_at']);
    prefs.setString('user_updated_at', user['user_data']['updated_at']);
    prefs.setString('user_category', user['user_data']['category']);
    prefs.setString('token', user['token']);
  }
  Future<void> _catalogo(BuildContext context)async {
            Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const HomeScreen(
          )),
        );
  }


  Future<void> _login(BuildContext context, String email, String password) async {
    if (email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Por favor, ingrese correo electrónico y contraseña'),
        ),
      );
      return;
    }

    try {
      final response = await http.post(
        Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/login'),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8'
        },
        body: jsonEncode(<String, String>{
          'user': email,
          'password': password,
        }),
      );
      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        _saveUserInfo(responseData);
        Navigator.push(
          // ignore: use_build_context_synchronously
          context,
          MaterialPageRoute(builder: (context) => const HomeScreen(
          )),
        );

      } else {
        // ignore: use_build_context_synchronously
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error al iniciar sesión, correo electrónico o contraseña incorrectos'),
          ),
        );
      }
    } catch (e) {
      // ignore: use_build_context_synchronously
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        color: Colors.grey[900],
        child: Center(
          child: SingleChildScrollView(  // Uso de SingleChildScrollView para evitar problemas con el teclado
            child: SizedBox(
              width: MediaQuery.of(context).size.width * 0.8,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Image.asset(
                    'web/assets/images/start_icon.png',
                    width: 300,
                    height: 300,
                  ),
                  const SizedBox(height: 40),

                  TextField(
                    controller: emailController,
                    decoration: const InputDecoration(
                      hintText: 'Correo o Teléfono',
                      prefixIcon: Icon(Icons.person),
                      hintStyle: TextStyle(color: Colors.white),
                    ),
                    style: const TextStyle(color: Colors.white),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(
                      hintText: 'Contraseña',
                      prefixIcon: Icon(Icons.lock),
                      hintStyle: TextStyle(color: Colors.white),
                    ),
                    style: const TextStyle(color: Colors.white),
                  ),
                  const SizedBox(height: 40),
                  ElevatedButton(
                    onPressed: () {
                      _login(context, emailController.text, passwordController.text);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),
                    child: const Text(
                      'Iniciar sesión',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                  const SizedBox(height: 40),
                  ElevatedButton(
                    onPressed: () {
                      _catalogo(context);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                    ),
                    child: const Text(
                      'Explorar el catálogo',
                      style: TextStyle(color: Colors.green),
                    ),
                  ),
                  const SizedBox(height: 20),
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed('/register');
                    },
                    child: const Text(
                      '¿No tienes una cuenta? Regístrate aquí',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (context) => ForgotPasswordScreen())
                      );
                    },
                    child: const Text(
                      '¿Olvidaste tu contraseña?',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
