import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:frescapp/api_routes.dart';

class ForgotPasswordScreen extends StatelessWidget {
  // ignore: use_super_parameters
  ForgotPasswordScreen({Key? key}) : super(key: key);

  final TextEditingController emailOrPhoneController = TextEditingController();

  Future<void> _sendResetPasswordRequest(BuildContext context, String emailOrPhone) async {
    if (emailOrPhone.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Por favor, ingrese su correo electrónico o teléfono'),
        ),
      );
      return;
    }

    try {
      final response = await http.post(
        Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/forgot_password'), // Endpoint para la solicitud de restablecimiento de contraseña
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8'
        },
        body: jsonEncode(<String, String>{
          'user': emailOrPhone,
        }),
      );
      if (response.statusCode == 200) {
        // ignore: use_build_context_synchronously
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Se ha enviado un mensaje al correo registrado con instrucciones para restablecer la contraseña'),
          ),
        );
      } else {
        // ignore: use_build_context_synchronously
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error al enviar la solicitud de restablecimiento de contraseña. Por favor, inténtelo de nuevo más tarde.'),
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
      appBar: AppBar(
        title: const Text('Restablecer Contraseña'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: emailOrPhoneController,
              decoration: const InputDecoration(
                hintText: 'Correo electrónico o Teléfono',
                prefixIcon: Icon(Icons.person),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                _sendResetPasswordRequest(context, emailOrPhoneController.text);
              },
              child: const Text('Enviar'),
            ),
          ],
        ),
      ),
    );
  }
}
