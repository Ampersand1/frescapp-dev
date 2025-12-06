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
import 'package:frescapp/screens/discounts/descuentos_page.dart';

class OrderDetailScreen extends StatefulWidget {
  final List<Product> productsInCart;
  final Order order;

  const OrderDetailScreen(
      {super.key, required this.productsInCart, required this.order});

  @override
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

      String message =
          'Hola, soy $name y mis datos son:\nEmail: $email\nTeléfono: $phone. Tengo la siguiente duda.';

      String encodedMessage = Uri.encodeComponent(message);
      String url = 'whatsapp://send?phone=$contactPhone&text=$encodedMessage';

      await launchUrlString(url);
    } catch (error) {
      if (kDebugMode) {
        print('Error opening WhatsApp: $error');
      }
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
    // -------------------------------
    // CÁLCULO REAL DE TOTALES
    // -------------------------------
    double finalTotal = 0;
    double totalSavings = 0;

    for (var product in widget.productsInCart) {
      double originalPrice = product.priceSale ?? 0;
      double finalPrice = product.finalPrice ?? originalPrice;
      bool hasDiscount = product.hasDiscount;

      if (hasDiscount) {
        totalSavings += (originalPrice - finalPrice) * (product.quantity ?? 0);
      }

      finalTotal += finalPrice * (product.quantity ?? 0);
    }

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
              // TOTAL
              Text(
                'Total: \$ ${NumberFormat('#,###').format(finalTotal)}',
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),

              // AHORRO
              if (totalSavings > 0) ...[
                const SizedBox(height: 5),
                Text(
                  'Ahorraste: \$ ${NumberFormat('#,###').format(totalSavings)}',
                  style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.green),
                ),
              ],

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
                  _confirmOrder(context, finalTotal, totalSavings);
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
          type: BottomNavigationBarType.fixed,
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
              icon: Icon(Icons.local_offer),
              label: 'Descuentos',
            ),
            const BottomNavigationBarItem(
              icon: Icon(Icons.message_rounded),
              label: 'WhatsApp',
            ),
          ],
          onTap: (int index) {
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
                () => Navigator.push(context,
                    MaterialPageRoute(builder: (context) => LoginScreen())),
              if (_userActive)
                () => Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) =>
                              ProfileScreen(order: widget.order)),
                    ),
              () => Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const DescuentosPage()),
                  ),
              () => _openWhatsApp(context),
            ];

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
      primer = DateTime(now.year, now.month, now.day + 3);
    } else {
      primer = DateTime(now.year, now.month, now.day + 1);
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
    return day.weekday != DateTime.sunday;
  }

  void _confirmOrder(
      BuildContext context, double calculatedTotal, double calculatedSavings) {
    if (selectedDeliverySlot == 'Horario de entrega' ||
        selectedPaymentMethod == 'Método de pago') {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
              'Por favor, seleccione fecha, horario de entrega y medio de pago.'),
        ),
      );
      return;
    }

    widget.order.products = widget.productsInCart;
    widget.order.discount = calculatedSavings;
    widget.order.total = calculatedTotal;
    widget.order.deliverySlot = selectedDeliverySlot!;
    widget.order.paymentMethod = selectedPaymentMethod!;
    widget.order.deliveryDate =
        DateFormat('yyyy-MM-dd').format(selectedDate);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            OrderConfirmationScreen(orderDetails: widget.order),
      ),
    ).catchError((error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al confirmar el pedido: $error'),
        ),
      );
    });
  }
}
