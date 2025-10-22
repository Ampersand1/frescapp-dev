import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:frescapp/screens/login_screen.dart';
import 'package:frescapp/api_routes.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _RegisterScreenState createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _documentController = TextEditingController();
  final TextEditingController _restaurantNameController = TextEditingController();
  final TextEditingController _addressController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();

  String? _selectedDocumentType;
  String? _selectedCustomerType;

  final List<String> documentTypes = ['', 'CC', 'NIT', 'PA', 'TI'];
  final List<String> customerTypes = ["Restaurante Ejecutivo","Restaurante Gourmet","Frutería","Panadería","Comidas Rápidas","Hogar","Instituciones"];

  String? _passwordErrorText;

  Future<void> _createUser() async {
    if (_nameController.text.isEmpty ||
        _selectedDocumentType == null ||
        _documentController.text.isEmpty ||
        _restaurantNameController.text.isEmpty ||
        _addressController.text.isEmpty ||
        _phoneController.text.isEmpty ||
        _emailController.text.isEmpty ||
        _passwordController.text.isEmpty ||
        _confirmPasswordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, complete todos los campos')),
      );
      return;
    }

    if (_passwordController.text != _confirmPasswordController.text) {
      setState(() {
        _passwordErrorText = 'Las contraseñas no coinciden';
      });
      return;
    }

    final Map<String, dynamic> userData = {
      'name': _nameController.text,
      'document_type': _selectedDocumentType,
      'document': _documentController.text,
      'restaurant_name': _restaurantNameController.text,
      'address': _addressController.text,
      'phone': _phoneController.text,
      'email': _emailController.text,
      'password': _passwordController.text,
      'status': 'active',
      'category': _selectedCustomerType,
      'created_at': DateTime.now().toString(),
      'updated_at': DateTime.now().toString(),
    };

    final response = await http.post(
      Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.customers}/customer'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(userData),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Usuario creado exitosamente')),
      );
      Navigator.push(
        // ignore: use_build_context_synchronously
        context,
        MaterialPageRoute(builder: (context) => LoginScreen()),
      );
    } else {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      String errorMessage = responseBody['message'] ?? 'Error al crear usuario';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(errorMessage)),
      );
      if (kDebugMode) {
        print('Error al crear usuario: $responseBody');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Registro de Usuario'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Nombre'),
                keyboardType: TextInputType.name,
                textInputAction: TextInputAction.next,
                autofocus: true,
                autocorrect: false,
                enableSuggestions: false,
              ),
              DropdownButtonFormField<String>(
                initialValue: _selectedDocumentType,
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedDocumentType = newValue;
                  });
                },
                items: documentTypes.map((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                decoration: const InputDecoration(labelText: 'Tipo de Documento'),
              ),
              TextField(
                controller: _documentController,
                decoration: const InputDecoration(labelText: 'Documento'),
                keyboardType: TextInputType.text,
                textInputAction: TextInputAction.next,
              ),
              TextField(
                controller: _restaurantNameController,
                decoration: const InputDecoration(labelText: 'Nombre del Restaurante'),
                keyboardType: TextInputType.text,
                textInputAction: TextInputAction.next,
              ),
              TextField(
                controller: _addressController,
                decoration: const InputDecoration(labelText: 'Dirección'),
                keyboardType: TextInputType.text,
                textInputAction: TextInputAction.next,
              ),
              TextField(
                controller: _phoneController,
                decoration: const InputDecoration(labelText: 'Teléfono'),
                keyboardType: TextInputType.phone,
                textInputAction: TextInputAction.next,
              ),
              TextField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email'),
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.next,
              ),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Contraseña'),
                keyboardType: TextInputType.visiblePassword,
                textInputAction: TextInputAction.next,
              ),
              TextField(
                controller: _confirmPasswordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Confirmar Contraseña',
                  errorText: _passwordErrorText,
                ),
                keyboardType: TextInputType.visiblePassword,
                textInputAction: TextInputAction.done,
                onChanged: (value) {
                  setState(() {
                    if (_passwordController.text == value) {
                      _passwordErrorText = null;
                    } else {
                      _passwordErrorText = 'Las contraseñas no coinciden';
                    }
                  });
                },
              ),
              DropdownButtonFormField<String>(
                initialValue: _selectedCustomerType,
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedCustomerType = newValue;
                  });
                },
                items: customerTypes.map((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                decoration: const InputDecoration(labelText: 'Tipo de Cliente'),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: _createUser,
                child: const Text('Crear Usuario'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _documentController.dispose();
    _restaurantNameController.dispose();
    _addressController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }
}
