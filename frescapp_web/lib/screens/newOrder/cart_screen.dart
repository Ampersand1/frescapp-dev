import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/orders/orders_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:frescapp/models/product.dart';
import 'package:frescapp/screens/newOrder/detail_cart_screen.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:frescapp/models/order.dart' as orden;
import 'package:frescapp/api_routes.dart';
import 'package:http/http.dart' as http;
import 'package:frescapp/screens/login_screen.dart';
import 'package:frescapp/screens/discounts/descuentos_page.dart';

class CartScreen extends StatefulWidget {
  final List<Product> productsInCart;
  final orden.Order order;

  const CartScreen(
      {super.key,
      required this.productsInCart,
      required void Function(int value) updateCounter,
      required this.order});

  @override
  // ignore: library_private_types_in_public_api
  _CartScreenState createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  late bool _userActive = false;

  @override
  void initState() {
    _checkTokenValidity();
    super.initState();
  }

  // --- LOGICA DE DESCUENTOS ---
  double _getProductDiscount(Product product) {
    if (product.name != null) {
      // Simulación de descuentos variados
      if (product.name!.length % 3 == 0) return 0.20; // 20%
      if (product.name!.length % 5 == 0) return 0.10; // 10%
    }
    return 0.0;
  }

  double _calculateDiscountedPrice(
      double originalPrice, double discountPercent) {
    return originalPrice * (1 - discountPercent);
  }
  // ---------------------------

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
    final List<Product> productsWithQuantity = widget.productsInCart
        .where((product) => product.quantity! > 0)
        .toList();

    double total = 0;
    double totalSavings = 0;

    // Calcular totales considerando descuentos
    for (var product in productsWithQuantity) {
      double originalPrice = (product.priceSale ?? 0).toDouble();
      double discountPercent = _getProductDiscount(product);
      double finalPrice = originalPrice;

      if (discountPercent > 0) {
        finalPrice =
            _calculateDiscountedPrice(originalPrice, discountPercent);
        totalSavings +=
            (originalPrice - finalPrice) * (product.quantity ?? 0);
      }

      total += finalPrice * (product.quantity ?? 0);
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tu Pedido'),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: productsWithQuantity.length,
              itemBuilder: (context, index) {
                final Product product = productsWithQuantity[index];

                // Variables locales para renderizado
                double originalPrice = (product.priceSale ?? 0).toDouble();
                double discountPercent = _getProductDiscount(product);
                bool hasDiscount = discountPercent > 0;
                double finalPrice = hasDiscount
                    ? _calculateDiscountedPrice(originalPrice, discountPercent)
                    : originalPrice;
                double subTotal = finalPrice * (product.quantity ?? 0);

                return ListTile(
                  leading: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      CircleAvatar(
                        backgroundColor: Colors.white,
                        backgroundImage: NetworkImage(product.image ?? ''),
                      ),
                      if (hasDiscount)
                        Positioned(
                          right: -2,
                          top: -2,
                          child: Container(
                            padding: const EdgeInsets.all(3),
                            decoration: const BoxDecoration(
                                color: Colors.yellow,
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black26,
                                    blurRadius: 2,
                                    offset: Offset(1, 1),
                                  )
                                ]),
                            child: Text(
                              '-${(discountPercent * 100).toInt()}%',
                              style: const TextStyle(
                                color: Colors.black,
                                fontSize: 8,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                  title: RichText(
                    text: TextSpan(
                      children: [
                        TextSpan(
                          text: '${product.name ?? ''} - ',
                          style: const TextStyle(
                            fontWeight: FontWeight.normal,
                            color: Colors.black,
                          ),
                        ),
                        // Lógica visual de precios
                        if (hasDiscount) ...[
                          TextSpan(
                            text:
                                '\nPrecio \$ ${NumberFormat('#,###').format(originalPrice)} ',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.grey,
                              decoration: TextDecoration.lineThrough,
                              fontSize: 12,
                            ),
                          ),
                          TextSpan(
                            text:
                                '\$ ${NumberFormat('#,###').format(finalPrice)}',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                        ] else ...[
                          TextSpan(
                            text:
                                '\nPrecio \$ ${NumberFormat('#,###').format(originalPrice)}',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.black,
                            ),
                          ),
                        ],
                        TextSpan(
                          text:
                              '\nSubtotal \$ ${NumberFormat('#,###').format(subTotal)}',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.black,
                          ),
                        ),
                      ],
                    ),
                  ),
                  subtitle: Text(product.category ?? ''),
                  onTap: () {
                    showDialog(
                      context: context,
                      builder: (context) {
                        return StatefulBuilder(
                          builder:
                              (BuildContext context, StateSetter setState) {
                            return AlertDialog(
                              title: Text(
                                product.name ?? "",
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 18,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              content: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Image.network(
                                    product.image ?? '',
                                    height: 200,
                                    width: 200,
                                  ),
                                  const SizedBox(height: 20),
                                  Text(
                                    product.name ?? "",
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  if (hasDiscount)
                                    Column(
                                      children: [
                                        Text(
                                          '\$ ${NumberFormat('#,###').format(originalPrice)}',
                                          style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              color: Colors.grey,
                                              decoration:
                                                  TextDecoration.lineThrough),
                                          textAlign: TextAlign.center,
                                        ),
                                        Text(
                                          '\$ ${NumberFormat('#,###').format(finalPrice)}',
                                          style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              color: Colors.green,
                                              fontSize: 16),
                                          textAlign: TextAlign.center,
                                        ),
                                      ],
                                    )
                                  else
                                    Text(
                                      ' \$  ${NumberFormat('#,###').format(originalPrice)}',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                  Text(
                                    product.category ?? "",
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ],
                              ),
                              actions: [
                                TextButton(
                                  onPressed: () {
                                    Navigator.of(context).pop();
                                  },
                                  child: const Text('Cerrar'),
                                ),
                              ],
                            );
                          },
                        );
                      },
                    );
                  },
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.remove),
                        onPressed: () {
                          setState(() {
                            if (product.quantity! > 0) {
                              product.quantity = product.quantity! - 1;
                            }
                          });
                        },
                      ),
                      Text(product.quantity.toString()),
                      IconButton(
                        icon: const Icon(Icons.add),
                        onPressed: () {
                          setState(() {
                            product.quantity = product.quantity! + 1;
                          });
                        },
                      ),
                    ],
                  ),
                );
              },
            ),

            const SizedBox(height: 10),

            // 1. TOTAL
            Padding(
              padding: const EdgeInsets.only(top: 16.0, left: 16.0, right: 16.0, bottom: 5.0),
              child: Text(
                'Total: \$ ${NumberFormat('#,###').format(total)}',
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ),

            // 2. AHORRO (CON TEXTO "Ahorraste: $...")
            if (totalSavings > 0)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Text(
                  'Ahorraste: \$ ${NumberFormat('#,###').format(totalSavings)}',
                  style: const TextStyle(
                      fontSize: 18, // Tamaño ligeramente más grande para resaltar
                      fontWeight: FontWeight.bold,
                      color: Colors.green),
                ),
              ),
            
            const SizedBox(height: 10),

            // BOTÓN CONFIRMAR
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  // Esto asegura que el texto sea ROJO cuando el botón está deshabilitado (onPressed es null)
                  disabledForegroundColor: Colors.red, 
                ),
                onPressed: total >= 100000
                    ? () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => OrderDetailScreen(
                                productsInCart: productsWithQuantity,
                                order: widget.order),
                          ),
                        );
                      }
                    : null,
                child: Text(
                  total >= 100000 
                    ? 'Confirmar Pedido' 
                    : 'Mínimo de compra \$ 100.000',
                  // Si prefieres forzar el estilo del texto directamente:
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: total >= 100000 ? null : Colors.red, // Rojo explícito si no cumple
                  ),
                ),
              ),
            ),
          ],
        ),
      ),

      // BOTTOM NAV
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
            // Lista de acciones
            List<VoidCallback> activeActions = [];
            
            // 0. Inicio
            activeActions.add(() => Navigator.push(context,
                MaterialPageRoute(builder: (context) => HomeScreen(order: widget.order))));
            
            // 1. Pedidos (si activo)
            if (_userActive) {
              activeActions.add(() => Navigator.push(context,
                  MaterialPageRoute(builder: (context) => OrdersScreen(order: widget.order))));
            }
            
            // 2. Login/Perfil
            if (!_userActive) {
              activeActions.add(() => Navigator.push(context,
                  MaterialPageRoute(builder: (context) => LoginScreen())));
            } else {
              activeActions.add(() => Navigator.push(context,
                  MaterialPageRoute(builder: (context) => ProfileScreen(order: widget.order))));
            }
            
            // 3. Descuentos
            activeActions.add(() => Navigator.push(context,
                MaterialPageRoute(builder: (context) => const DescuentosPage())));
            
            // 4. WhatsApp
            activeActions.add(() => _openWhatsApp(context));

            if (index < activeActions.length) {
              activeActions[index]();
            }
          },
        ),
      ),
    );
  }
}