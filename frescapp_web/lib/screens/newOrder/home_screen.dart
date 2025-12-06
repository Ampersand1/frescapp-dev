import 'dart:async';
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
import 'package:frescapp/services/cart_service.dart';

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
  late Order order;
  ConfigService configService = ConfigService(http.Client());

  // Debounce search
  Timer? _searchDebounce;
  String _lastQuery = '';

  // Anti-double-tap processing set (skus being updated)
  final Set<String> _processingSkus = {};

  // Small optimization: reuse NumberFormat
  final NumberFormat _numFmt = NumberFormat('#,###');

  @override
  void initState() {
    super.initState();
    _checkTokenValidity();
    order = widget.order ?? Order(products: []);
    name = order.customerName ?? 'Frescapp';
    getUserInfo();
    getInitialProducts();
  }

  @override
  void dispose() {
    _searchDebounce?.cancel();
    super.dispose();
  }

  Future<void> getUserInfo() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      final Map<String, dynamic> configData =
          await configService.getConfigData();
      // guard against missing keys
      if (configData['delivery_cost'] is double) {
        prefs.setDouble('delivery_cost', configData['delivery_cost'] as double);
      }
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

    if (kDebugMode) {
      print("==== EMAIL PARA PETICIÓN ====");
      print(safeEmail);
    }

    // Traemos productos + descuentos ya aplicados
    try {
      allProducts = await productService.getProducts(safeEmail);

      // Update CartService snapshots with loaded products (keeps prices & images fresh)
      for (var p in allProducts) {
        if (p.sku != null && p.sku!.isNotEmpty) {
          try {
            CartService().updateSnapshotFromProduct(p);
          } catch (_) {
            // ignore snapshot errors for malformed product
          }
        }
      }

      setState(() {
        displayedProducts = allProducts.toList();
      });

      // After products are loaded, sync with cart (if user already has items)
      loadOrder(widget.order ?? Order());
    } catch (e) {
      if (kDebugMode) print('Error cargando productos iniciales: $e');
      setState(() {
        allProducts = [];
        displayedProducts = [];
      });
    }
  }

  // -------------------------------------
  // FILTER + DEBOUNCE
  void filterProducts(String query) {
    _searchDebounce?.cancel();
    _searchDebounce = Timer(const Duration(milliseconds: 250), () {
      final normalizedQuery = removeDiacritics(query.toLowerCase());
      // avoid redundant work
      if (normalizedQuery == _lastQuery) return;
      _lastQuery = normalizedQuery;

      setState(() {
        if (normalizedQuery.isEmpty) {
          displayedProducts = allProducts.toList();
        } else {
          displayedProducts = allProducts.where((Product product) {
            final productName =
                removeDiacritics((product.name ?? '').toLowerCase());
            final productCategory =
                removeDiacritics((product.category ?? '').toLowerCase());
            return productName.contains(normalizedQuery) ||
                productCategory.contains(normalizedQuery);
          }).toList();
        }
      });
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

  // -------------------------------------
  // QUANTITY HANDLERS using CartService (source-of-truth)
  void increaseQuantity(Product product) async {
    final sku = product.sku ?? '';
    if (sku.isEmpty) return;

    if (_processingSkus.contains(sku)) return;
    _processingSkus.add(sku);

    try {
      CartService().addProduct(product);
      // update local snapshot's displayed quantity quickly
      _syncQuantities();
    } finally {
      _processingSkus.remove(sku);
    }
  }

  void decreaseQuantity(Product product) async {
    final sku = product.sku ?? '';
    if (sku.isEmpty) return;

    if (_processingSkus.contains(sku)) return;
    _processingSkus.add(sku);

    try {
      CartService().removeProduct(product);
      _syncQuantities();
    } finally {
      _processingSkus.remove(sku);
    }
  }

  // Sync displayed products with CartService quantities and snapshots.
  // This is cheap: reads in-memory structures.
  void _syncQuantities() {

    setState(() {
      // For each product in allProducts, set quantity from CartService snapshot (qtyForSku)
      for (var p in allProducts) {
        final sku = p.sku ?? '';
        if (sku.isEmpty) {
          p.quantity = 0;
          continue;
        }
        p.quantity = CartService().qtyForSku(sku);
        // Optionally refresh discount/finalPrice from snapshot if needed:
        // CartService keeps product snapshots; we could update p.finalPrice for UI freshness
        // but to avoid aliasing we rely on updateSnapshotFromProduct when products reload
        // If you prefer to reflect snapshot values immediately:
        final snapshotList =
            CartService().items.where((c) => c.sku == sku).toList();
        if (snapshotList.isNotEmpty) {
          final snap = snapshotList.first;
          p.finalPrice = snap.finalPrice ?? p.finalPrice;
          p.hasDiscount = snap.hasDiscount || p.hasDiscount;
          p.savingsPct = snap.savingsPct ?? p.savingsPct;
        }
      }

      // Update the displayed list (respect existing filter)
      displayedProducts = displayedProducts.map((dp) {
        // find updated product by sku
        final updated =
            allProducts.firstWhere((ap) => ap.sku == dp.sku, orElse: () => dp);
        return updated;
      }).toList();

      // Update productCounter (sum of quantities)
      CartService().items.fold<int>(0, (s, p) => s + (p.quantity ?? 0));
      // keep the order.order.products consistent with cart snapshot
      widget.order?.products = CartService().items;
      // assign counter to order if desired (not required)
      // productCounter variable not declared (we use order.products length/count where needed)
      // but to keep parity with previous UI we store in 'name' only when necessary
      // For UI labels that used productCounter previously, you can compute on the fly:
      // int productCounter = totalCount;
      if (kDebugMode) {
        // debug print
        // print('Cart total items: $totalCount');
      }
    });
  }

  Future<void> loadOrder(Order order) async {
    // When navigating back from Descuentos or Cart, refresh quantities from CartService
    _syncQuantities();

    // Also, sync widget.order products with cart snapshot
    widget.order?.products = CartService().items;
    // Update name and other user-related fields kept elsewhere
    setState(() {
      name = widget.order?.customerName ?? name;
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
        setState(() {
          _userActive = true;
        });
      } else {
        setState(() {
          _userActive = false;
        });
      }
    } else {
      setState(() {
        _userActive = false;
      });
    }
  }

  // Función auxiliar para preparar la orden antes de navegar
  void _prepareOrderForNavigation() {
    widget.order?.products = CartService().items;
  }

  @override
  Widget build(BuildContext context) {
    // small local getter for counter
    final int productCounter =
        CartService().items.fold<int>(0, (s, p) => s + (p.quantity ?? 0));

    return Scaffold(
      appBar: AppBar(
        title: Text(name),
        actions: [
          Stack(
            alignment: Alignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.shopping_cart),
                onPressed: () {
                  // Sincronizamos antes de ir al carrito
                  _prepareOrderForNavigation();
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => CartScreen(
                        productsInCart: CartService().items,
                        updateCounter: (v) => _syncQuantities(),
                        order: widget.order ?? Order(),
                      ),
                    ),
                  ).then((_) => _syncQuantities());
                },
              ),
              if (productCounter > 0)
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
                      productCounter.toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                )
            ],
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
              child: displayedProducts.isEmpty
                  ? const Center(child: Text('No se encontraron productos.'))
                  : ListView.builder(
                      itemCount: displayedProducts.length,
                      itemBuilder: (context, index) {
                        final product = displayedProducts[index];
                        final hasDiscount = product.hasDiscount;
                        final discountPercent = product.savingsPct ?? 0.0;
                        final originalPrice = product.priceSale ?? 0.0;
                        final finalPrice =
                            product.finalPrice ?? product.priceSale ?? 0.0;
                        final qty = CartService().qtyForSku(product.sku ?? '');

                        return ListTile(
                          leading: Stack(
                            clipBehavior: Clip.none,
                            children: [
                              CircleAvatar(
                                radius: 30,
                                backgroundColor: Colors.white,
                                backgroundImage:
                                    NetworkImage(product.image ?? ''),
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
                                        '\n\$ ${_numFmt.format(originalPrice)} ',
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
                                      fontSize: 14,
                                    ),
                                  ),
                                ] else
                                  TextSpan(
                                    text:
                                        '\n\$ ${_numFmt.format(originalPrice)}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: Colors.black,
                                    ),
                                  ),
                              ],
                            ),
                          ),
                          subtitle: Text(product.category ?? ''),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              ElevatedButton(
                                onPressed: () {
                                  // Disable rapid taps
                                  if (_processingSkus.contains(product.sku)) return;
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
                                padding:
                                    const EdgeInsets.symmetric(horizontal: 8.0),
                                child: Text(
                                  (qty).toString(),
                                  style: const TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold),
                                ),
                              ),
                              ElevatedButton(
                                onPressed: () {
                                  // Disable rapid taps
                                  if (_processingSkus.contains(product.sku)) return;
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
                                      title: Text(product.name ?? '',
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
                                                product.image ?? '',
                                                height: 200,
                                                width: 200,
                                                errorBuilder: (_, __, ___) =>
                                                    Container(
                                                  height: 200,
                                                  width: 200,
                                                  color: Colors.grey.shade200,
                                                  child:
                                                      const Icon(Icons.image_not_supported),
                                                ),
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
                                          Text(product.name ?? '',
                                              style: const TextStyle(
                                                  fontWeight: FontWeight.bold),
                                              textAlign: TextAlign.center),
                                          if (hasDiscount)
                                            Column(
                                              children: [
                                                Text(
                                                  '\$ ${_numFmt.format(originalPrice)}',
                                                  style: const TextStyle(
                                                    fontWeight: FontWeight.bold,
                                                    color: Colors.grey,
                                                    decoration:
                                                        TextDecoration.lineThrough,
                                                  ),
                                                  textAlign: TextAlign.center,
                                                ),
                                                Text(
                                                  '\$ ${_numFmt.format(finalPrice)}',
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
                                                ' \$  ${_numFmt.format(product.priceSale ?? 0)}',
                                                style: const TextStyle(
                                                    fontWeight: FontWeight.bold),
                                                textAlign: TextAlign.center),
                                          Text(product.category ?? '',
                                              style: const TextStyle(
                                                  fontWeight: FontWeight.bold),
                                              textAlign: TextAlign.center),
                                          Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              ElevatedButton(
                                                onPressed: () {
                                                  if (_processingSkus.contains(product.sku)) return;
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
                                                padding:
                                                    const EdgeInsets.symmetric(horizontal: 8.0),
                                                child: Text(
                                                  (CartService().qtyForSku(product.sku ?? '')).toString(),
                                                  style: const TextStyle(
                                                      fontSize: 16, fontWeight: FontWeight.bold),
                                                ),
                                              ),
                                              ElevatedButton(
                                                onPressed: () {
                                                  if (_processingSkus.contains(product.sku)) return;
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
          type: BottomNavigationBarType.fixed, // Asegura que se vean todos los labels
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
            _prepareOrderForNavigation();

            List<VoidCallback> activeActions = [];

            // 1. Inicio (Recargar Home)
            activeActions.add(() => Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                    builder: (context) => HomeScreen(order: widget.order))));

            // 2. Pedidos (si activo)
            if (_userActive) {
              activeActions.add(() => Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                      builder: (context) => OrdersScreen(order: widget.order))));
            }

            // 3. Login (si inactivo) o Perfil (si activo)
            if (!_userActive) {
              activeActions.add(() => Navigator.pushReplacement(context,
                  MaterialPageRoute(builder: (context) => LoginScreen())));
            } else {
              activeActions.add(() => Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                      builder: (context) =>
                          ProfileScreen(order: widget.order))));
            }

            // 4. Descuentos (AQUI SE PASA EL ORDER)
            activeActions.add(() => Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                    builder: (context) => DescuentosPage(order: widget.order))));

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
