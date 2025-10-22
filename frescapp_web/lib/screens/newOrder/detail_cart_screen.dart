import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/newOrder/order_confirmation_screen.dart';
import 'package:frescapp/screens/orders/orders_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:frescapp/models/order.dart';
import 'package:frescapp/models/product.dart';
import 'package:frescapp/services/order_service.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:http/http.dart' as http;
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/screens/login_screen.dart';

class OrderDetailScreen extends StatefulWidget {
  final List<Product> productsInCart;
  final Order order;

  const OrderDetailScreen({super.key, required this.productsInCart,required  this.order});

  @override
  // ignore: library_private_types_in_public_api
  _OrderDetailScreenState createState() => _OrderDetailScreenState();
}

class _OrderDetailScreenState extends State<OrderDetailScreen> {
  late DateTime selectedDate;
  String? selectedDeliverySlot;
  String? selectedPaymentMethod;
  late bool _userActive = false;
  late List<String> paymentMethods = [];
  late List<String> deliverySlots = [];
  final OrderService orderService = OrderService();
  @override
  void initState() {
    super.initState();
    selectedDate = DateTime.now().add(const Duration(days: 1));
    selectedDeliverySlot = 'Horario de entrega';
    selectedPaymentMethod = 'Método de pago';
    getOrderDetailsFromSharedPreferences();
    _checkTokenValidity();

  }

  void getOrderDetailsFromSharedPreferences() async {
    try {
      final SharedPreferences prefs = await SharedPreferences.getInstance();
      setState(() {
        // Actualiza las listas después de obtener las preferencias compartidas
        deliverySlots = prefs.getStringList('delivery_slots') ?? [];
        paymentMethods = prefs.getStringList('payments_method') ?? [];
      });
    } catch (e) {
      if (kDebugMode) {
        print('Error al obtener preferencias compartidas: $e');
      }
    }
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

Future<void> _checkTokenValidity() async {
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
  @override
  Widget build(BuildContext context) {
    double total = widget.productsInCart.fold(
        0, (sum, product) => sum + ((product.priceSale ?? 0) * (product.quantity ?? 0)));
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detalle del Pedido'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                'Total: \$ ${NumberFormat('#,###').format(total)}',
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              const Text(
                'Fecha de Entrega:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: 200,
                child: ElevatedButton(
                  onPressed: () {
                    _selectDate(context);
                  },
                  child: Text(
                    '${selectedDate.day}/${selectedDate.month}/${selectedDate.year}',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Horario de Entrega:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Column(
                children: deliverySlots.map((slot) {
                  return RadioListTile<String>(
                    title: Text(slot),
                    value: slot,
                    groupValue: selectedDeliverySlot,
                    onChanged: (String? newValue) {
                      setState(() {
                        selectedDeliverySlot = newValue;
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              const Text(
                'Medio de Pago:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Column(
                children: paymentMethods.map((method) {
                  return RadioListTile<String>(
                    title: Text(method),
                    value: method,
                    groupValue: selectedPaymentMethod,
                    onChanged: (String? newValue) {
                      setState(() {
                        selectedPaymentMethod = newValue;
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  _confirmOrder(context);
                },
                child: const Text('Confirmar Pedido'),
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
                        builder: (context) => HomeScreen(order: widget.order)),
                  ),
              if (_userActive)
                () => Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) =>
                              OrdersScreen(order: widget.order)),
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
                              ProfileScreen(order: widget.order)),
                    ),
              () => _openWhatsApp(context),
            ];

            // Ejecutar la acción correspondiente si existe
            if (index < actions.length) {
              actions[index]();
            }
          },
        ),
      ),
    );
  }

  Future<void> _selectDate(BuildContext context) async {
    DateTime now = DateTime.now();
    late DateTime primer;
    final DateTime lastDate = DateTime(now.year, now.month, now.day + 7);

    if (now.weekday == DateTime.friday && now.hour >= 18) {
      // Es viernes después de las 6 p.m.
      primer = DateTime(now.year, now.month,
          now.day + 3); // Primer día disponible es el lunes
    } else {
      // Otro día de la semana o viernes antes de las 6 p.m.
      primer = DateTime(now.year, now.month,
          now.day + 1); // El primer día disponible es el siguiente
    }

    final DateTime? picked = await showDatePicker(
      context: context,
      firstDate: primer,
      lastDate: lastDate,
      selectableDayPredicate: _isSelectableDate,
    );

    if (picked != null && picked != selectedDate) {
      setState(() {
        selectedDate = picked;
      });
    }
  }

  bool _isSelectableDate(DateTime day) {
    // Evitar seleccionar domingos
    if (day.weekday == DateTime.sunday) {
      return false;
    }
    return true;
  }

  void _confirmOrder(BuildContext context) {
    // Verificar que se hayan seleccionado la fecha de entrega, el horario de entrega y el medio de pago
    if (selectedDeliverySlot == 'Horario de entrega' || selectedPaymentMethod == 'Método de pago') {
      // Mostrar un mensaje de advertencia si no se han seleccionado todos los campos
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Por favor, seleccione fecha, horario de entrega y medio de pago.'),
        ),
      );
      return; // Salir del método sin continuar con la confirmación del pedido
    }
    widget.order.products = widget.productsInCart;
    widget.order.discount = 0;
    widget.order.total = widget.productsInCart.fold(
          0.0, (sum, product) => sum! + ((product.priceSale ?? 0) * (product.quantity ?? 0)));
    widget.order.deliverySlot = selectedDeliverySlot!;
    widget.order.paymentMethod = selectedPaymentMethod!;
    widget.order.deliveryDate = DateFormat('yyyy-MM-dd').format(selectedDate);
    // Enviar el objeto Order al servicio
      Navigator.push(
        context,
        MaterialPageRoute(
            builder: (context) =>
                OrderConfirmationScreen(orderDetails: widget.order)),
      ).catchError((error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al confirmar el pedido: $error'),
        ),
      );
    });
  }
}
