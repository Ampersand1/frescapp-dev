import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/orders/orders_screen.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:frescapp/models/order.dart';

class ProfileScreen extends StatefulWidget {
    final Order? order;
  const ProfileScreen({super.key, this.order});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late TextEditingController _nameController = TextEditingController();
  late TextEditingController _phoneController = TextEditingController();
  late TextEditingController _documentController = TextEditingController();
  late String _selectedDocumentType = '';
  late TextEditingController _addressController = TextEditingController();
  late TextEditingController _restaurantNameController =
      TextEditingController();
  late TextEditingController _emailController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchUserData();
  }


void _openWhatsApp(BuildContext context) async {
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  try {
    String name = prefs.getString('user_name') ?? '';
    String email = prefs.getString('user_email') ?? '';
    String phone = prefs.getString('user_phone') ?? '';
    String contactPhone = prefs.getString('contact_phone') ?? '';

    String message = 'Hola, soy $name y mis datos son:\nEmail: $email\nTeléfono: $phone. Tengo la siguiente duda.';

    // Codificar el mensaje para que se pueda enviar correctamente en la URL
    String encodedMessage = Uri.encodeComponent(message);

    // Construir la URL para abrir WhatsApp con el mensaje predefinido
    String url = 'whatsapp://send?phone=$contactPhone&text=$encodedMessage';

    // Lanzar la URL para abrir WhatsApp
    await launchUrlString(url);
  } catch (error) {
    if (kDebugMode) {
      print('Error opening WhatsApp: $error');
    }
    // ignore: use_build_context_synchronously
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Error al abrir WhatsApp.'),
      ),
    );
  }
}


  Future<void> _fetchUserData() async {
    try {
      final SharedPreferences prefs = await SharedPreferences.getInstance();
      late String customerId = prefs.getString('user_id') ?? '';
      final response = await http.get(Uri.parse(
          '${ApiRoutes.baseUrl}${ApiRoutes.customers}/customer/$customerId'));
      if (response.statusCode == 200) {
        final userData = jsonDecode(response.body);
        setState(() {
          _nameController = TextEditingController(text: userData['name']);
          _phoneController = TextEditingController(text: userData['phone']);
          _documentController =
              TextEditingController(text: userData['document']);
          _selectedDocumentType = userData['document_type'];
          _addressController = TextEditingController(text: userData['address']);
          _restaurantNameController =
              TextEditingController(text: userData['restaurant_name']);
          _emailController = TextEditingController(text: userData['email']);
        });
      } else {
        throw Exception('Failed to load user data');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error fetching user data: $e');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Perfil'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildInfoField('Nombre', _nameController),
              _buildInfoField('Teléfono', _phoneController),
              Row(
                children: [
                  Expanded(
                    child: _buildInfoField('Documento', _documentController),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _buildDocumentTypeDropdown(),
                  ),
                ],
              ),
              _buildInfoField('Dirección', _addressController),
              _buildInfoField(
                  'Nombre del restaurante', _restaurantNameController),
              _buildInfoField('Correo electrónico', _emailController),
              const SizedBox(height: 10),
              SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      // Abrir la modal para cambiar la contraseña
                      _showChangePasswordModal(context);
                    },
                    child: const Text('Cambiar contraseña'),
                  )),
              const SizedBox(height: 10),
              SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      // Guardar cambios en los datos del usuario
                      _updateUserData(context, {
                        'name': _nameController.text,
                        'phone': _phoneController.text,
                        'document': _documentController.text,
                        'document_type': _selectedDocumentType,
                        'address': _addressController.text,
                        'restaurant_name': _restaurantNameController.text,
                        'email': _emailController.text,
                      });
                    },
                    child: const Text('Guardar cambios'),
                  )),
              const SizedBox(height: 10),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    // Cerrar sesión
                    _logout(context);
                  },
                  style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red.shade200),
                  child: const Text('Cerrar sesión'),
                ),
              )
            ],
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: BottomNavigationBar(
          currentIndex: 2,
          selectedItemColor:
              Colors.lightGreen.shade900, // Color de los iconos seleccionados
          unselectedItemColor:
              Colors.grey, // Color de los iconos no seleccionados
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home),
              label: 'Inicio',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.shopping_cart),
              label: 'Pedidos',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person),
              label: 'Perfil',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.chat), // Icono de WhatsApp
              label: 'WhatsApp', // Etiqueta para el botón
            ),
          ],
          onTap: (int index) {
            switch (index) {
              case 0:
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => HomeScreen(order: widget.order)),
                );
                break;
              case 1:
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => OrdersScreen(order: widget.order)),
                );
                break;
              case 2:
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => ProfileScreen(order: widget.order)),
                );
                break;
              case 3:
                _openWhatsApp(context); // Función para abrir WhatsApp
                break;
            }
          },
        ),
      ),
    );
  }

  Widget _buildInfoField(String label, TextEditingController controller) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 5),
        TextFormField(
          controller: controller,
          readOnly: false,
        ),
        const SizedBox(height: 20),
      ],
    );
  }

  Widget _buildDocumentTypeDropdown() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Tipo de documento',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 5),
        DropdownButton<String>(
          value: _selectedDocumentType,
          onChanged: (String? newValue) {
            setState(() {
              _selectedDocumentType = newValue!;
            });
          },
          items: <String>['', 'CC', 'NIT', 'PA', 'TI']
              .map<DropdownMenuItem<String>>(
                (String value) => DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                ),
              )
              .toList(),
        ),
        const SizedBox(height: 20),
      ],
    );
  }

  void _showChangePasswordModal(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        String newPassword = '';
        String confirmPassword = '';
        return AlertDialog(
          title: const Text('Cambiar contraseña'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                onChanged: (value) {
                  newPassword = value;
                },
                decoration:
                    const InputDecoration(labelText: 'Nueva contraseña'),
                obscureText: true,
              ),
              TextField(
                onChanged: (value) {
                  confirmPassword = value;
                },
                decoration: const InputDecoration(
                    labelText: 'Confirmar nueva contraseña'),
                obscureText: true,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () {
                _updatePassword(context, newPassword, confirmPassword);
              },
              child: const Text('Guardar'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _updatePassword(
      BuildContext context, String newPassword, String confirmPassword) async {
    // Verificar que las contraseñas coincidan
    if (newPassword == confirmPassword) {
      try {
        final SharedPreferences prefs = await SharedPreferences.getInstance();
        final String token = prefs.getString('token') ?? '';
        final response = await http.post(
          Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/change_password'),
          headers: <String, String>{
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer $token',
          },
          body: jsonEncode({"password": newPassword}),
        );
        if (response.statusCode == 200) {
          // ignore: use_build_context_synchronously
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Datos actualizados correctamente')),
          );
          _fetchUserData(); // Actualizar los datos mostrados en la pantalla
        } else {
          throw Exception('Failed to update user data');
        }
      } catch (e) {
        if (kDebugMode) {
          print('Error updating user data: $e');
        }
      }
      // ignore: use_build_context_synchronously
      Navigator.of(context).pop(); // Cerrar el diálogo
    } else {
      // Mostrar mensaje de error si las contraseñas no coinciden
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Las contraseñas no coinciden')),
      );
    }
  }

  void _updateUserData(
      BuildContext context, Map<String, dynamic> userData) async {
    try {
      final SharedPreferences prefs = await SharedPreferences.getInstance();
      late String customerId = prefs.getString('user_id') ?? '';
      final String token = prefs.getString('token') ?? '';
      final response = await http.put(
        Uri.parse(
            '${ApiRoutes.baseUrl}${ApiRoutes.customers}/customers/$customerId'),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(userData),
      );
      if (response.statusCode == 200) {
        // ignore: use_build_context_synchronously
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Datos actualizados correctamente')),
        );
        _fetchUserData(); // Actualizar los datos mostrados en la pantalla
      } else {
        throw Exception('Failed to update user data');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error updating user data: $e');
      }
    }
  }

void _logout(BuildContext context) async {
  try {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    final String? token = prefs.getString('token');

    // Realizar solicitud de logout si el token existe
    if (token != null) {
      final response = await http.post(
        Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/logout'),
        headers: {
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to logout');
      }
    }

    // Limpiar preferencias y caché
    await prefs.clear();

    // Redirigir al usuario a la pantalla de inicio de sesión
    Navigator.of(context).pushReplacementNamed('/login');
  } catch (e) {
    if (kDebugMode) {
      print('Error during logout: $e');
    }

    // En caso de error, redirigir igualmente al login
    Navigator.of(context).pushReplacementNamed('/login');
  }
}

}
