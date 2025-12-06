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
import 'package:frescapp/services/cart_service.dart';

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
  final NumberFormat _numFmt = NumberFormat('#,###');

  @override
  void initState() {
    _checkTokenValidity();
    super.initState();
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

  // Helpers que operan sobre CartService
  void _increase(Product product) {
    try {
      CartService().addProduct(product);
      setState(() {}); // fuerza re-render con snapshot actualizado
    } catch (e) {
      if (kDebugMode) print('Error adding product to cart: $e');
    }
  }

  void _decrease(Product product) {
    try {
      CartService().removeProduct(product);
      setState(() {}); // fuerza re-render con snapshot actualizado
    } catch (e) {
      if (kDebugMode) print('Error removing product from cart: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    // list snapshot from CartService (source of truth)
    final List<Product> productsWithQuantity =
        CartService().items.where((p) => (p.quantity ?? 0) > 0).toList();

    // totals from CartService (accurate with snapshots)
    final double total = CartService().total;
    final double totalSavings = CartService().savings;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tu Pedido'),
        actions: [
          Stack(
            alignment: Alignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.home),
                onPressed: () {
                  // Mantén coherencia con HomeScreen: pasar order actualizado
                  widget.order.products = CartService().items;
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (context) => HomeScreen(order: widget.order),
                    ),
                  );
                },
              ),
              // contador pequeño opcional: muestra número total de items
              if (CartService().items.fold<int>(0, (s, p) => s + (p.quantity ?? 0)) >
                  0)
                Positioned(
                  right: 6,
                  top: 6,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      CartService().items
                          .fold<int>(0, (s, p) => s + (p.quantity ?? 0))
                          .toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                )
            ],
          )
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Si el carrito está vacío mostramos mensaje
            if (productsWithQuantity.isEmpty)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 40),
                child: Column(
                  children: [
                    const Icon(Icons.remove_shopping_cart, size: 64, color: Colors.grey),
                    const SizedBox(height: 12),
                    const Text('Tu carrito está vacío',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 6),
                    TextButton(
                      onPressed: () {
                        widget.order.products = CartService().items;
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(
                              builder: (context) => HomeScreen(order: widget.order)),
                        );
                      },
                      child: const Text('Volver al catálogo'),
                    ),
                  ],
                ),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: productsWithQuantity.length,
                itemBuilder: (context, index) {
                  final Product product = productsWithQuantity[index];

                  final double originalPrice = product.priceSale ?? 0;
                  final double finalPrice = product.finalPrice ?? originalPrice;
                  final bool hasDiscount = product.hasDiscount;
                  final double discountPct = product.savingsPct ?? 0;
                  final int qty = product.quantity ?? 0;
                  final double subTotal = finalPrice * qty;

                  return ListTile(
                    leading: Stack(
                      clipBehavior: Clip.none,
                      children: [
                        CircleAvatar(
                          backgroundColor: Colors.white,
                          backgroundImage: NetworkImage(product.image ?? ''),
                          // mostrar placeholder si falla
                          onBackgroundImageError: (_, __) {},
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
                              ),
                              child: Text(
                                '-${discountPct.toInt()}%',
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
                          if (hasDiscount) ...[
                            TextSpan(
                              text:
                                  '\nPrecio \$ ${_numFmt.format(originalPrice)} ',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.grey,
                                decoration: TextDecoration.lineThrough,
                                fontSize: 12,
                              ),
                            ),
                            TextSpan(
                              text:
                                  '\$ ${_numFmt.format(finalPrice)}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.green,
                              ),
                            ),
                          ] else ...[
                            TextSpan(
                              text:
                                  '\nPrecio \$ ${_numFmt.format(originalPrice)}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.black,
                              ),
                            ),
                          ],
                          TextSpan(
                            text:
                                '\nSubtotal \$ ${_numFmt.format(subTotal)}',
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
                                      errorBuilder: (_, __, ___) => Container(
                                        height: 200,
                                        width: 200,
                                        color: Colors.grey.shade200,
                                        child: const Icon(Icons.image_not_supported),
                                      ),
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
                                            '\$ ${_numFmt.format(originalPrice)}',
                                            style: const TextStyle(
                                                fontWeight: FontWeight.bold,
                                                color: Colors.grey,
                                                decoration:
                                                    TextDecoration.lineThrough),
                                            textAlign: TextAlign.center,
                                          ),
                                          Text(
                                            '\$ ${_numFmt.format(finalPrice)}',
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
                                        ' \$  ${_numFmt.format(originalPrice)}',
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
                          onPressed: qty > 0
                              ? () {
                                  _decrease(product);
                                }
                              : null,
                        ),
                        Text(qty.toString()),
                        IconButton(
                          icon: const Icon(Icons.add),
                          onPressed: () {
                            _increase(product);
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
              padding: const EdgeInsets.only(
                  top: 16.0, left: 16.0, right: 16.0, bottom: 5.0),
              child: Text(
                'Total: \$ ${_numFmt.format(total)}',
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ),

            // 2. AHORRO (CON TEXTO "Ahorraste: $...")
            if (totalSavings > 0)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Text(
                  'Ahorraste: \$ ${_numFmt.format(totalSavings)}',
                  style: const TextStyle(
                      fontSize:
                          18, // Tamaño ligeramente más grande para resaltar
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
                onPressed: total >= 100000 && productsWithQuantity.isNotEmpty
                    ? () {
                        // Aseguramos que la orden tenga la lista actual del carrito
                        widget.order.products = CartService().items;
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => OrderDetailScreen(
                                productsInCart: CartService().items,
                                order: widget.order),
                          ),
                        ).then((_) {
                          // refresca tras volver
                          setState(() {});
                        });
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
                    color: total >= 100000
                        ? null
                        : Colors.red, // Rojo explícito si no cumple
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
            activeActions.add(() => Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => HomeScreen(order: widget.order))));

            // 1. Pedidos (si activo)
            if (_userActive) {
              activeActions.add(() => Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) =>
                          OrdersScreen(order: widget.order))));
            }

            // 2. Login/Perfil
            if (!_userActive) {
              activeActions.add(() => Navigator.push(context,
                  MaterialPageRoute(builder: (context) => LoginScreen())));
            } else {
              activeActions.add(() => Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) =>
                          ProfileScreen(order: widget.order))));
            }

            // 3. Descuentos
            activeActions.add(() => Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const DescuentosPage())));

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
