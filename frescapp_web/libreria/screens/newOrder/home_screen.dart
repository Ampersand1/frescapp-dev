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
  List<Product> productsInCart = [];
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
    // Obtiene el correo electrónico del usuario, o asigna 'undefined' si no existe
    final String userEmail = prefs.getString('user_email') ?? 'undefined';
    // Llama al servicio de productos con el correo obtenido
    allProducts = await productService.getProducts(userEmail);

    setState(() {
      displayedProducts = allProducts.toList();
    });

    loadOrder(widget.order ?? Order());
  }

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
      product.quantity = (product.quantity! + 1);
      productCounter++;
      if (!productsInCart.contains(product)) {
        productsInCart.add(product);
      }
    });
  }

  void decreaseQuantity(Product product) {
    setState(() {
      if (product.quantity! > 0) {
        product.quantity = (product.quantity! - 1);
        productCounter--;
        if (product.quantity == 0) {
          productsInCart.remove(product);
        }
      }
    });
  }

  void updateCounter(int value) {
    setState(() {
      productCounter = value;
    });
  }

  Future<void> loadOrder(Order order) async {
    if (widget.order == null) {
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
    } else {
      for (var product in allProducts) {
        var matchingProduct = order.products!.firstWhere(
          (orderProduct) => orderProduct.sku == product.sku,
          orElse: () => Product(
              sku: product.sku,
              name: product.name,
              category: product.category,
              quantity: 0,
              priceSale: product.priceSale,
              image: product.image),
        );
        if (matchingProduct.quantity != null) {
          product.quantity = matchingProduct.quantity;
        }
      }

      setState(() {
        productsInCart = order.products!;
        productCounter =
            productsInCart.fold(0, (sum, item) => sum + (item.quantity as int));
        userAddress = order.deliveryAddress ?? '';
        name = order.customerName ?? 'Frescapp';
        displayedProducts = allProducts.toList();
      });
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
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => CartScreen(
                    productsInCart: productsInCart,
                    updateCounter: updateCounter,
                    order: order,
                  ),
                ),
              );
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
                  return ListTile(
                    leading: CircleAvatar(
                      backgroundColor: Colors.white,
                      backgroundImage: NetworkImage(product.image as String),
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
                          TextSpan(
                            text:
                                '\n \$ ${NumberFormat('#,###').format(product.priceSale)}',
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
                            padding: const EdgeInsets.all(
                                5), // Reduce el espacio interno
                            backgroundColor: const Color.fromARGB(221, 223, 98, 89),
                            minimumSize:
                                const Size(30, 30), // Tamaño mínimo del botón
                            maximumSize:
                                const Size(30, 30), // Tamaño máximo del botón
                          ),
                          child: const Icon(Icons.remove,
                              color: Colors.white,
                              size: 16), // Ícono más pequeño
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 8.0),
                          child: Text(
                            product.quantity.toString(),
                            style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight
                                    .bold), // Ajusta el tamaño del texto
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
                            padding: const EdgeInsets.all(
                                5), // Reduce el espacio interno
                            backgroundColor: const Color.fromARGB(255, 97, 143, 99),
                            minimumSize:
                                const Size(30, 30), // Tamaño mínimo del botón
                            maximumSize:
                                const Size(30, 30), // Tamaño máximo del botón
                          ),
                          child: const Icon(Icons.add,
                              color: Colors.white,
                              size: 16), // Ícono más pequeño
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
                                    Image.network(
                                      product.image as String,
                                      height: 200,
                                      width: 200,
                                    ),
                                    const SizedBox(height: 20),
                                    Text(product.name as String,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.bold),
                                        textAlign: TextAlign.center),
                                    Text(
                                      ' \$  ${NumberFormat('#,###').format(product.priceSale)}',
                                      style: const TextStyle(
                                          fontWeight: FontWeight.bold),
                                      textAlign: TextAlign.center,
                                    ),
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
                            padding: const EdgeInsets.all(
                                5), // Reduce el espacio interno
                            backgroundColor: const Color.fromARGB(221, 223, 98, 89),
                            minimumSize:
                                const Size(30, 30), // Tamaño mínimo del botón
                            maximumSize:
                                const Size(30, 30), // Tamaño máximo del botón
                          ),
                          child: const Icon(Icons.remove,
                              color: Colors.white,
                              size: 16), // Ícono más pequeño
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 8.0),
                          child: Text(
                            product.quantity.toString(),
                            style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight
                                    .bold), // Ajusta el tamaño del texto
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
                            padding: const EdgeInsets.all(
                                5), // Reduce el espacio interno
                            backgroundColor: const Color.fromARGB(255, 97, 143, 99),
                            minimumSize:
                                const Size(30, 30), // Tamaño mínimo del botón
                            maximumSize:
                                const Size(30, 30), // Tamaño máximo del botón
                          ),
                          child: const Icon(Icons.add,
                              color: Colors.white,
                              size: 16), // Ícono más pequeño
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
}
