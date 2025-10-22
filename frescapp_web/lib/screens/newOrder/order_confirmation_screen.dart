import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../../models/order.dart';
import 'home_screen.dart';
import '../orders/orders_screen.dart';
import '../profile/profile_screen.dart';
import '../../services/order_service.dart';
import '../../api_routes.dart';
import '../../services/discount_service.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';
import '../login_screen.dart';

// ignore: must_be_immutable
class OrderConfirmationScreen extends StatefulWidget {
  static List<DropdownMenuItem<String>> listDocumentType = [];

  final Order orderDetails;
  const OrderConfirmationScreen({super.key, required this.orderDetails});

  @override
  // ignore: library_private_types_in_public_api
  _OrderConfirmationScreenState createState() =>
      _OrderConfirmationScreenState();
}

class _OrderConfirmationScreenState extends State<OrderConfirmationScreen> {
  final TextEditingController _codeController = TextEditingController();
  late bool _userActive = false;
  final TextEditingController _user = TextEditingController();
  final TextEditingController _nameRestaurant = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController =
      TextEditingController();
  String? _passwordErrorText;
  @override
  void initState() {
    super.initState();
    getOrderDetailsFromSharedPreferences();
    _checkTokenValidity2();
  }

  Future<Order> getOrderDetailsFromSharedPreferences() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      if(prefs.getString('user_id') != null){
        final String customerId = prefs.getString('user_id') ?? '';
        final response = await http.get(Uri.parse(
            '${ApiRoutes.baseUrl}${ApiRoutes.customers}/customer/$customerId'));
        if (response.statusCode == 200) {
          var userData = jsonDecode(response.body);
          widget.orderDetails.customerName = userData['name'];
          widget.orderDetails.customerPhone = userData['phone'];
          widget.orderDetails.customerDocumentNumber = userData['document'];
          widget.orderDetails.customerDocumentType = userData['document_type'];
          widget.orderDetails.deliveryAddress = userData['address'];
          widget.orderDetails.customerEmail = userData['email'];
          widget.orderDetails.deliveryCost =
              (prefs.getDouble('delivery_cost') ?? 0) as double?;
        } else {
          throw Exception('Failed to load user data');
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error fetching user data: $e');
      }
    }

    return widget.orderDetails;
  }

  Future<bool> validateCode(String code, String email) async {
    final DiscountService discountService = DiscountService();
    double? descuento =
        await discountService.validateCode(code, email) as double?;
    setState(() {
      widget.orderDetails.discount =
          ((descuento! / 100) * widget.orderDetails.total!);
      widget.orderDetails.total =
          widget.orderDetails.total! - widget.orderDetails.discount!;
    });
    return widget.orderDetails.discount as double > 0.0;
  }

  String generateOrderNumber() {
    Random random = Random();
    int orderNumber = random.nextInt(90000) + 10000;
    return orderNumber.toString();
  }

  String getCurrentDateTimeString() {
    DateTime now = DateTime.now();
    return now.toIso8601String();
  }

  void _openWhatsApp(BuildContext context) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      String name = prefs.getString('user_name') ?? '';
      String email = prefs.getString('user_email') ?? '';
      String phone = prefs.getString('user_phone') ?? '';
      String contactPhone = prefs.getString('contact_phone') ?? '';

      String message =
          'Hola, soy $name y mis datos son:\nEmail: $email\nTeléfono: $phone. Tengo la siguiente duda.';

      String encodedMessage = Uri.encodeComponent(message);
      String url = 'whatsapp://send?phone=$contactPhone&text=$encodedMessage';

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

  Future<void> sendOrderDetailsToService(Order orderDetails) async {
    if (orderDetails.orderNumber == null ||
        orderDetails.orderNumber!.isEmpty ||
        orderDetails.orderNumber == '') {
      orderDetails.orderNumber = generateOrderNumber();
      orderDetails.createdAt = getCurrentDateTimeString();
      orderDetails.updatedAt = getCurrentDateTimeString();
    }
    final OrderService orderService = OrderService();
    try {
      await orderService.createOrder(
          orderDetails.orderNumber ?? '', orderDetails);
    } catch (e) {
      if (kDebugMode) {
        print('Error al enviar detalles del pedido al servicio: $e');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return _buildOrderConfirmationScreen(context);
  }

  Widget _buildOrderConfirmationScreen(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: const Text('Confirmar Pedido'),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Center(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const Text(
                  'Detalles del Pedido',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 32),
                Text(
                  'Fecha de Entrega: ${widget.orderDetails.deliveryDate ?? ''}',
                  style: const TextStyle(fontSize: 16),
                ),
                const SizedBox(height: 16),
                Text(
                  'Horario de Entrega: ${widget.orderDetails.deliverySlot ?? ''}',
                  style: const TextStyle(fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  'Medio de Pago: ${widget.orderDetails.paymentMethod ?? ''}',
                  style: const TextStyle(fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  'Costo de envío: \$ ${widget.orderDetails.deliveryCost ?? 0}',
                  style: const TextStyle(fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  'Descuento: \$ ${(NumberFormat('#,###').format(widget.orderDetails.discount as double))}',
                  style: const TextStyle(fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  'Total: \$ ${NumberFormat('#,###').format(widget.orderDetails.total!)}',
                  style: const TextStyle(fontSize: 16),
                ),
                const SizedBox(height: 24),
                _buildCustomerInfoForm(),
                //const SizedBox(height: 16),
                //_buildValidationSection(),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () async {
                    bool isTokenValid = await _checkTokenValidity();

                    if (isTokenValid) {
                      // Token válido: Crear solo el pedido
                      await sendOrderDetailsToService(widget.orderDetails);
                      // ignore: use_build_context_synchronously
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Pedido creado exitosamente'),
                        ),
                      );
                    } else {
                      // Token no válido: Crear usuario y luego el pedido
                      await _createUser();
                      await sendOrderDetailsToService(widget.orderDetails);
                      // ignore: use_build_context_synchronously
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                              'Usuario creado y pedido realizado exitosamente'),
                        ),
                      );
                    }

                    final response = await http.post(
                      Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/login'),
                      headers: <String, String>{
                        'Content-Type': 'application/json; charset=UTF-8'
                      },
                      body: jsonEncode(<String, String>{
                        'user': _user.text,
                        'password': _confirmPasswordController.text,
                      }),
                    );
                    if (response.statusCode == 200) {
                      final responseData = jsonDecode(response.body);

                      _saveUserInfo(responseData);
                      Navigator.push(
                        // ignore: use_build_context_synchronously
                        context,
                        MaterialPageRoute(
                            builder: (context) => const HomeScreen()),
                      );
                    }
                  },
                  child: FutureBuilder<bool>(
                    future: _checkTokenValidity(),
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const CircularProgressIndicator();
                      } else if (snapshot.hasData && snapshot.data == true) {
                        return const Text('Realizar pedido');
                      } else {
                        return const Text('Crear usuario y realizar pedido');
                      }
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
        bottomNavigationBar: SafeArea(
          child: BottomNavigationBar(
            currentIndex: 0,
            selectedItemColor: Colors.lightGreen.shade900,
            unselectedItemColor: Colors.grey,
            items: [
              const BottomNavigationBarItem(
                icon: Icon(Icons.home),
                label: 'Inicio',
              ),
              if (_userActive)
                const BottomNavigationBarItem(
                  icon: Icon(Icons.shopping_cart),
                  label: 'Pedidos',
                ),
              if (!_userActive)
                const BottomNavigationBarItem(
                  icon: Icon(Icons.person),
                  label: 'Login',
                ),
              if (_userActive)
                const BottomNavigationBarItem(
                  icon: Icon(Icons.person),
                  label: 'Perfil',
                ),
              const BottomNavigationBarItem(
                icon: Icon(Icons.message_rounded),
                label: 'WhatsApp',
              ),
            ],
            onTap: (int index) {
              // Lista de funciones para cada botón
              final actions = [
                () => Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) =>
                              HomeScreen(order: widget.orderDetails)),
                    ),
                if (_userActive)
                  () => Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) =>
                                OrdersScreen(order: widget.orderDetails)),
                      ),
                if (!_userActive)
                  () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => LoginScreen()),
                      ),
                if (_userActive)
                  () => Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) =>
                                ProfileScreen(order: widget.orderDetails)),
                      ),
                () => _openWhatsApp(context),
              ];

              // Ejecutar la acción correspondiente si existe
              if (index < actions.length) {
                actions[index]();
              }
            },
          ),
        ));
  }

  Future<void> _saveUserInfo(dynamic user) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    prefs.setString('user_id', user['user_data']['_id']);
    prefs.setString('user_phone', user['user_data']['phone']);
    prefs.setString('user_name', user['user_data']['name']);
    prefs.setString('user_document', user['user_data']['document']);
    prefs.setString('user_document_type', user['user_data']['document_type']);
    prefs.setString('user_address', user['user_data']['address']);
    prefs.setString(
        'user_restaurant_name', user['user_data']['restaurant_name']);
    prefs.setString('user_email', user['user_data']['email']);
    prefs.setString('user_status', user['user_data']['status']);
    prefs.setString('user_created_at', user['user_data']['created_at']);
    prefs.setString('user_updated_at', user['user_data']['updated_at']);
    prefs.setString('user_category', user['user_data']['category']);
    prefs.setString('token', user['token']);
  }

  Future<bool> _checkTokenValidity() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    // Verifica si hay un token y devuelve true si es válido, de lo contrario, devuelve false
    if (token != null) {
      final response = await http.post(
        Uri.parse(
            '${ApiRoutes.baseUrl}${ApiRoutes.user}/check_token'), // Endpoint para verificar el token

        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer $token'
        },
      );
      if (response.statusCode == 200) {}
      return response.statusCode == 200;
    } else {
      return false;
    }
  }

  Future<void> _checkTokenValidity2() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token != null) {
      final response = await http.post(
        Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/check_token'),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
          'Authorization': 'Bearer $token',
        },
      );

      setState(() {
        _userActive = response.statusCode == 200;
      });
    } else {
      setState(() {
        _userActive = false;
      });
    }
  }

  Future<void> _createUser() async {
    try {
      final response = await http.post(
        Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.customers}/customer'),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode({
          'name': widget.orderDetails.customerName,
          'restaurant_name': _nameRestaurant.text,
          'phone': widget.orderDetails.customerPhone,
          'email': widget.orderDetails.customerEmail,
          'document': widget.orderDetails.customerDocumentNumber,
          'document_type': widget.orderDetails.customerDocumentType,
          'address': widget.orderDetails.deliveryAddress,
          'status': 'active',
          'user': _user.text,
          'category': 'Restaurante Ejecutivo',
          'password': _passwordController.text,
          'created_at': DateTime.now().toString(),
          'updated_at': DateTime.now().toString()
        }),
      );

      if (response.statusCode == 201) {
        print('Usuario creado exitosamente');
      } else {
        throw Exception('Error al crear usuario');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error al crear usuario: $e');
      }
    }
  }

  Widget _buildCustomerInfoForm() {
    return FutureBuilder<Order>(
      future: getOrderDetailsFromSharedPreferences(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        } else if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        } else if (!snapshot.hasData || snapshot.data == null) {
          return const Text('No se encontraron datos de facturación.');
        } else {
          Order orderDetails = snapshot.data!;
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Información de Facturación',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.customerName ?? '',
                decoration: const InputDecoration(
                  labelText: 'Nombre',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.customerName = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _nameRestaurant,
                decoration: const InputDecoration(
                  labelText: 'Nombre Restaurante',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                initialValue: orderDetails.customerDocumentType ?? '',
                decoration: const InputDecoration(
                  labelText: 'Tipo de Documento',
                  border: OutlineInputBorder(),
                ),
                onChanged: (String? newValue) {
                  orderDetails.customerDocumentType = newValue;
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
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.customerDocumentNumber ?? '',
                decoration: const InputDecoration(
                  labelText: 'Número de Documento',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.customerDocumentNumber = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.customerPhone ?? '',
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Número de Teléfono',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.customerPhone = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.customerEmail ?? '',
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Correo Electrónico',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.customerEmail = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.deliveryAddress ?? '',
                decoration: const InputDecoration(
                  labelText: 'Dirección de Entrega',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.deliveryAddress = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.deliveryAddressDetails ?? '',
                decoration: const InputDecoration(
                  labelText: 'Detalle de Dirección',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.deliveryAddressDetails = value;
                },
              ),
              if (!_userActive) const SizedBox(height: 16),
              if (!_userActive) TextFormField(
                controller: _user,
                decoration: const InputDecoration(
                  labelText: 'Usuario',
                  border: OutlineInputBorder(),
                ),
              ),
              if (!_userActive) const SizedBox(height: 16),
              if (!_userActive) TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Contraseña',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.visiblePassword,
                textInputAction: TextInputAction.next,
              ),
              if (!_userActive) const SizedBox(height: 16),
              if (!_userActive) TextField(
                controller: _confirmPasswordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Confirmar Contraseña',
                  border: const OutlineInputBorder(),
                  errorText: _passwordErrorText,
                ),
                keyboardType: TextInputType.visiblePassword,
                textInputAction: TextInputAction.done,
              ),
            ],
          );
        }
      },
    );
  }
}
