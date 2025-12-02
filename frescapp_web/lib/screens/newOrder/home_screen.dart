import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/models/order.dart';
import 'package:frescapp/models/product.dart';
import 'package:frescapp/screens/login_screen.dart';
import 'package:frescapp/services/product_service.dart';
import 'package:frescapp/screens/newOrder/cart_screen.dart';
import 'package:frescapp/screens/orders/orders_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:intl/intl.dart';
import 'package:frescapp/services/config_service.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher_string.dart';
import 'package:frescapp/screens/discounts/descuentos_page.dart';
import 'package:frescapp/utils/cart_sync.dart';

// ignore: must_be_immutable
class HomeScreen extends StatefulWidget {
  final Order? order;
  const HomeScreen({super.key, this.order});
  @override
  // ignore: library_private_types_in_public_api
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ProductService productService = ProductService();
  List<Product> displayedProducts = [];
  late bool _userActive = false;
  List<Product> allProducts = [];
  late String userAddress = '';
  late String name = 'Frescapp';
  late num productCounter = 0;
  late Order order;
  ConfigService configService = ConfigService(http.Client());

  @override
  void initState() {
    super.initState();
    _checkTokenValidity();
    order = widget.order ?? Order(products: []);
    name = order.customerName ?? 'Frescapp';
    getUserInfo();
    getInitialProducts();
  }

  Future<void> getUserInfo() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      final Map<String, dynamic> configData =
          await configService.getConfigData();
      prefs.setDouble('delivery_cost', configData['delivery_cost'] as double);
      prefs.setStringList('delivery_slots',
          List<String>.from(configData['delivery_slots'] ?? []));
      prefs.setStringList('payments_method',
          List<String>.from(configData['payments_method'] ?? []));
      prefs.setStringList('document_type',
          List<String>.from(configData['document_type'] ?? []));
      prefs.setString('contact_phone', configData['contact_phone'] ?? '');
      prefs.setString('server_ip', configData['server_ip'] ?? '');
      setState(() {
        userAddress = prefs.getString('user_address') ?? 'Frescapp';
      });
    } catch (e) {
      if (kDebugMode) {
        print('Error al obtener los datos de configuración: $e');
      }
    }
  }

  Future<void> getInitialProducts() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    final String? userEmail = prefs.getString('user_email');

    final String safeEmail =
        (userEmail == null || userEmail.isEmpty) ? 'undefined' : userEmail;

    print("==== EMAIL PARA PETICIÓN ====");
    print(safeEmail);

    // Traemos productos + descuentos ya aplicados
    allProducts = await productService.getProducts(safeEmail);

    setState(() {
      displayedProducts = allProducts.toList();
      syncProducts(allProducts, order);
    });

    loadOrder(widget.order ?? Order());
  }

  // -------------------------------------

  void filterProducts(String query) {
    final normalizedQuery = removeDiacritics(query.toLowerCase());
    setState(() {
      if (query.isEmpty) {
        displayedProducts = allProducts.toList();
      } else {
        displayedProducts = allProducts.where((Product product) {
          final productName =
              removeDiacritics((product.name as String).toLowerCase());
          final productCategory =
              removeDiacritics((product.category as String).toLowerCase());
          return productName.contains(normalizedQuery) ||
              productCategory.contains(normalizedQuery);
        }).toList();
      }
    });
  }

  String removeDiacritics(String str) {
    return str
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u');
  }

  void increaseQuantity(Product product) {
    setState(() {
      product.quantity = (product.quantity ?? 0) + 1;
      updateOrder(product);
      productCounter++;
    });
  }

  void decreaseQuantity(Product product) {
    setState(() {
      if ((product.quantity ?? 0) > 0) {
        product.quantity = (product.quantity ?? 0) - 1;
        updateOrder(product);
        productCounter--;
      }
    });
  }

  void updateOrder(Product product) {
    if (order.products == null) order.products = [];

    int index = order.products!.indexWhere((p) => p.sku == product.sku);

    if (index != -1) {
      if ((product.quantity ?? 0) > 0) {
        order.products![index].quantity = product.quantity;
      } else {
        order.products!.removeAt(index);
      }
    } else if ((product.quantity ?? 0) > 0) {
      order.products!.add(product);
    }
  }

  void updateCounter(int value) {
    setState(() {
      productCounter = value;
    });
  }

  Future<void> loadOrder(Order order) async {
    // Si widget.order viene lleno (por ejemplo, al volver de Descuentos), usamos eso
    if (widget.order != null && (widget.order?.products?.isNotEmpty ?? false)) {
      // Sincronizar la lista local de productos (allProducts) con las cantidades de la orden
      for (var product in allProducts) {
        var matchingProduct = widget.order!.products!.firstWhere(
          (orderProduct) => orderProduct.sku == product.sku,
          orElse: () => Product(sku: "dummy"),
        );
        if (matchingProduct.sku != "dummy") {
          product.quantity = matchingProduct.quantity;
        } else {
          product.quantity = 0;
        }
      }
    }
    // Lógica original de carga de usuario...
    else if (widget.order == null) {
      final SharedPreferences prefs = await SharedPreferences.getInstance();
      if (prefs.getString('user_id') != null) {
        final customerId = prefs.getString('user_id') ?? '';
        final response = await http.get(Uri.parse(
            '${ApiRoutes.baseUrl}${ApiRoutes.customers}/customer/$customerId'));
        if (response.statusCode == 200) {
          final userData = jsonDecode(response.body);
          setState(() {
            widget.order?.customerName = userData['name'] as String;
            widget.order?.customerPhone = userData['phone'] as String;
            widget.order?.customerDocumentNumber =
                userData['document'] as String;
            widget.order?.customerDocumentType =
                userData['document_type'] as String;
            widget.order?.deliveryAddress = userData['address'] as String;
            widget.order?.customerEmail = userData['email'] as String;
          });
        }
      }
    }

    setState(() {
      // Actualizar contador
      productCounter =
          order.products?.fold(0, (sum, item) => sum! + (item.quantity ?? 0)) ??
              0;
      userAddress = order.deliveryAddress ?? '';
      name = order.customerName ?? 'Frescapp';
      displayedProducts = allProducts.toList();
    });
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
          'Authorization': 'Bearer $token'
        },
      );
      if (response.statusCode == 200) {
        _userActive = true;
      } else {
        _userActive = false;
      }
    } else {
      _userActive = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(name),
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart),
            onPressed: () {
              // Sincronizamos antes de ir al carrito
              order = syncOrderProducts(allProducts, order);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => CartScreen(
                    productsInCart: order.products ?? [],
                    updateCounter: updateCounter,
                    order: order,
                  ),
                ),
              ).then((_) {
                setState(() {
                  syncProducts(allProducts, order);
                  productCounter = order.products?.fold(
                        0,
                        (sum, item) => sum! + (item.quantity ?? 0),
                      ) ??
                      0;
                });
              });
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.all(10),
              child: TextField(
                onChanged: filterProducts,
                decoration: const InputDecoration(
                  hintText: 'Buscar productos...',
                  prefixIcon: Icon(Icons.search),
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: displayedProducts.length,
                itemBuilder: (context, index) {
                  Product product = displayedProducts[index];
                  bool hasDiscount = product.hasDiscount;
                  double discountPercent = product.savingsPct ?? 0.0;
                  double originalPrice = product.priceSale ?? 0.0;
                  double finalPrice =
                      product.finalPrice ?? product.priceSale ?? 0.0;

                  return ListTile(
                    leading: Stack(
                      clipBehavior: Clip.none,
                      children: [
                        CircleAvatar(
                          radius: 30,
                          backgroundColor: Colors.white,
                          backgroundImage:
                              NetworkImage(product.image as String),
                        ),
                        if (hasDiscount)
                          Positioned(
                            right: -2,
                            top: -2,
                            child: Container(
                              padding: const EdgeInsets.all(4),
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
                                '-${(discountPercent).toInt()}%',
                                style: const TextStyle(
                                  color: Colors.black,
                                  fontSize: 10,
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
                            text: '${product.name} - ',
                            style: const TextStyle(
                              fontWeight: FontWeight.normal,
                              color: Colors.black,
                            ),
                          ),
                          if (hasDiscount) ...[
                            TextSpan(
                              text:
                                  '\n\$ ${NumberFormat('#,###').format(originalPrice)} ',
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
                                fontSize: 14,
                              ),
                            ),
                          ] else
                            TextSpan(
                              text:
                                  '\n\$ ${NumberFormat('#,###').format(originalPrice)}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.black,
                              ),
                            ),
                        ],
                      ),
                    ),
                    subtitle: Text(product.category as String),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        ElevatedButton(
                          onPressed: () {
                            setState(() {
                              decreaseQuantity(product);
                            });
                          },
                          style: ElevatedButton.styleFrom(
                            shape: const CircleBorder(),
                            padding: const EdgeInsets.all(5),
                            backgroundColor:
                                const Color.fromARGB(221, 223, 98, 89),
                            minimumSize: const Size(30, 30),
                            maximumSize: const Size(30, 30),
                          ),
                          child: const Icon(Icons.remove,
                              color: Colors.white, size: 16),
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 8.0),
                          child: Text(
                            product.quantity.toString(),
                            style: const TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ),
                        ElevatedButton(
                          onPressed: () {
                            setState(() {
                              increaseQuantity(product);
                            });
                          },
                          style: ElevatedButton.styleFrom(
                            shape: const CircleBorder(),
                            padding: const EdgeInsets.all(5),
                            backgroundColor:
                                const Color.fromARGB(255, 97, 143, 99),
                            minimumSize: const Size(30, 30),
                            maximumSize: const Size(30, 30),
                          ),
                          child: const Icon(Icons.add,
                              color: Colors.white, size: 16),
                        ),
                      ],
                    ),
                    onTap: () {
                      showDialog(
                        context: context,
                        builder: (context) {
                          return StatefulBuilder(
                            builder:
                                (BuildContext context, StateSetter setState) {
                              return AlertDialog(
                                title: Text(product.name as String,
                                    style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 18),
                                    textAlign: TextAlign.center),
                                content: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Stack(
                                      clipBehavior: Clip.none,
                                      alignment: Alignment.topRight,
                                      children: [
                                        Image.network(
                                          product.image as String,
                                          height: 200,
                                          width: 200,
                                        ),
                                        if (hasDiscount)
                                          Positioned(
                                            right: 10,
                                            top: 10,
                                            child: Container(
                                              padding: const EdgeInsets.all(8),
                                              decoration: const BoxDecoration(
                                                color: Colors.yellow,
                                                shape: BoxShape.circle,
                                              ),
                                              child: Text(
                                                '-${(discountPercent).toInt()}%',
                                                style: const TextStyle(
                                                  color: Colors.black,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ),
                                          ),
                                      ],
                                    ),
                                    const SizedBox(height: 20),
                                    Text(product.name as String,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.bold),
                                        textAlign: TextAlign.center),
                                    if (hasDiscount)
                                      Column(
                                        children: [
                                          Text(
                                            '\$ ${NumberFormat('#,###').format(originalPrice)}',
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              color: Colors.grey,
                                              decoration:
                                                  TextDecoration.lineThrough,
                                            ),
                                            textAlign: TextAlign.center,
                                          ),
                                          Text(
                                            '\$ ${NumberFormat('#,###').format(finalPrice)}',
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              color: Colors.green,
                                              fontSize: 18,
                                            ),
                                            textAlign: TextAlign.center,
                                          ),
                                        ],
                                      )
                                    else
                                      Text(
                                          ' \$  ${NumberFormat('#,###').format(product.priceSale)}',
                                          style: const TextStyle(
                                              fontWeight: FontWeight.bold),
                                          textAlign: TextAlign.center),
                                    Text(product.category as String,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.bold),
                                        textAlign: TextAlign.center),
                                    Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        ElevatedButton(
                                          onPressed: () {
                                            setState(() {
                                              decreaseQuantity(product);
                                            });
                                          },
                                          style: ElevatedButton.styleFrom(
                                            shape: const CircleBorder(),
                                            padding: const EdgeInsets.all(5),
                                            backgroundColor:
                                                const Color.fromARGB(
                                                    221, 223, 98, 89),
                                            minimumSize: const Size(30, 30),
                                            maximumSize: const Size(30, 30),
                                          ),
                                          child: const Icon(Icons.remove,
                                              color: Colors.white, size: 16),
                                        ),
                                        Padding(
                                          padding: const EdgeInsets.symmetric(
                                              horizontal: 8.0),
                                          child: Text(
                                            product.quantity.toString(),
                                            style: const TextStyle(
                                                fontSize: 16,
                                                fontWeight: FontWeight.bold),
                                          ),
                                        ),
                                        ElevatedButton(
                                          onPressed: () {
                                            setState(() {
                                              increaseQuantity(product);
                                            });
                                          },
                                          style: ElevatedButton.styleFrom(
                                            shape: const CircleBorder(),
                                            padding: const EdgeInsets.all(5),
                                            backgroundColor:
                                                const Color.fromARGB(
                                                    255, 97, 143, 99),
                                            minimumSize: const Size(30, 30),
                                            maximumSize: const Size(30, 30),
                                          ),
                                          child: const Icon(Icons.add,
                                              color: Colors.white, size: 16),
                                        ),
                                      ],
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
                  );
                },
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: BottomNavigationBar(
          currentIndex: 0,
          selectedItemColor: Colors.lightGreen.shade900,
          unselectedItemColor: Colors.grey,
          type: BottomNavigationBarType
              .fixed, // Asegura que se vean todos los labels
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
            // IMPORTANTE: Sincronizar el estado del carrito antes de salir del Home
            order = syncOrderProducts(allProducts, order);

            List<VoidCallback> activeActions = [];

            // 1. Inicio (Recargar Home)
            activeActions.add(() => Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                    builder: (context) => HomeScreen(order: order))));

            // 2. Pedidos (si activo)
            if (_userActive) {
              activeActions.add(() => Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                      builder: (context) => OrdersScreen(order: order))));
            }

            // 3. Login (si inactivo) o Perfil (si activo)
            if (!_userActive) {
              activeActions.add(() => Navigator.pushReplacement(context,
                  MaterialPageRoute(builder: (context) => LoginScreen())));
            } else {
              activeActions.add(() => Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                      builder: (context) => ProfileScreen(order: order))));
            }

            // 4. Descuentos (AQUI ESTABA EL ERROR, AHORA SE PASA EL ORDER)
            activeActions.add(() => Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                    builder: (context) => DescuentosPage(order: order))));

            // 5. WhatsApp
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
