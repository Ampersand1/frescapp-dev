import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/models/order.dart';
import 'package:frescapp/models/product.dart';
import 'package:frescapp/services/product_service.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/orders/orders_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:frescapp/screens/login_screen.dart';
import 'package:frescapp/screens/newOrder/cart_screen.dart';
import 'package:frescapp/services/cart_service.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:http/http.dart' as http;

class DescuentosPage extends StatefulWidget {
  final Order? order;
  const DescuentosPage({super.key, this.order});

  @override
  State<DescuentosPage> createState() => _DescuentosPageState();
}

class _DescuentosPageState extends State<DescuentosPage> {
  final Color verdePrincipal = const Color(0xFF5E6B4E);
  final Color fondo = const Color(0xFFF8F8E8);
  final TextStyle fontStyle = const TextStyle(fontFamily: 'Poppins');

  final ProductService productService = ProductService();
  final TextEditingController _searchController = TextEditingController();

  bool _isLoading = true;
  bool _userActive = false;
  String searchQuery = '';

  List<Product> allProducts = [];
  late Order currentOrder;

  @override
  void initState() {
    super.initState();
    _checkTokenValidity();

    // Order solo se usa para navegación, ya NO para el carrito
    currentOrder = widget.order ?? Order(products: []);

    getInitialProducts();
  }

  Future<void> getInitialProducts() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    final String userEmail = prefs.getString('user_email') ?? 'undefined';

    try {
      List<Product> fetchedProducts =
          await productService.getProducts(userEmail);

      // Actualizar snapshots de CartService con los productos cargados
      for (var p in fetchedProducts) {
        if (p.sku != null && p.sku!.isNotEmpty) {
          try {
            CartService().updateSnapshotFromProduct(p);
          } catch (_) {}
        }
      }

      setState(() {
        allProducts = fetchedProducts;
        _syncWithCart();
        _isLoading = false;
      });
    } catch (e) {
      if (kDebugMode) print("Error cargando productos: $e");
      setState(() => _isLoading = false);
    }
  }

  // Sincroniza cantidades de la UI con CartService
  void _syncWithCart() {
    for (var p in allProducts) {
      p.quantity = CartService().qtyForSku(p.sku ?? '');
    }
  }

  // Incrementar usando CartService como única fuente de verdad
  void increaseQuantity(Product product) {
    CartService().addProduct(product);
    setState(_syncWithCart);
  }

  // Decrementar usando CartService
  void decreaseQuantity(Product product) {
    CartService().removeProduct(product);
    setState(_syncWithCart);
  }

  // Contador global real del carrito
  int get productCounter {
    return CartService()
        .items
        .fold<int>(0, (sum, item) => sum + (item.quantity ?? 0));
  }

  Future<void> _checkTokenValidity() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    if (token != null) {
      try {
        final response = await http.post(
          Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/check_token'),
          headers: {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer $token'
          },
        );
        setState(() => _userActive = response.statusCode == 200);
      } catch (e) {
        setState(() => _userActive = false);
      }
    }
  }

  void _openWhatsApp(BuildContext context) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    String contactPhone = prefs.getString('contact_phone') ?? '';
    String url =
        'whatsapp://send?phone=$contactPhone&text=${Uri.encodeComponent("Hola, tengo una duda.")}';
    await launchUrlString(url);
  }

  // Back → regresar a Home con un Order actualizado
  Future<bool> _onWillPop() async {
    widget.order?.products = CartService().items;

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
          builder: (context) =>
              HomeScreen(order: widget.order ?? Order(products: CartService().items))),
      (Route<dynamic> route) => false,
    );
    return false;
  }

  // Navegación segura
  void _handleNavigation(int index) {
    widget.order?.products = CartService().items;

    if (index == 0) {
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(
            builder: (context) =>
                HomeScreen(order: widget.order ?? Order(products: CartService().items))),
        (Route<dynamic> route) => false,
      );
      return;
    }

    if (index == 5) {
      _openWhatsApp(context);
      return;
    }

    Widget? nextScreen;

    if (_userActive) {
      if (index == 1) nextScreen = OrdersScreen(order: widget.order);
      if (index == 3) nextScreen = ProfileScreen(order: widget.order);
    } else {
      if (index == 2) nextScreen = LoginScreen();
    }

    if (nextScreen != null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => nextScreen!),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final productosFiltrados = allProducts.where((p) {
      final bool matchesSearch =
          (p.name ?? '').toLowerCase().contains(searchQuery.toLowerCase());
      final bool hasDiscount = p.hasDiscount;
      return matchesSearch && hasDiscount;
    }).toList();

    final categorias =
        productosFiltrados.map((p) => p.category ?? 'Varios').toSet().toList();

    int currentIndex = _userActive ? 3 : 2;

    return WillPopScope(
      onWillPop: _onWillPop,
      child: Scaffold(
        backgroundColor: fondo,
        appBar: AppBar(
          title: Text("PromFres", style: fontStyle),
          backgroundColor: verdePrincipal,
          foregroundColor: Colors.white,
          centerTitle: true,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: _onWillPop,
          ),
          actions: [
            Stack(
              children: [
                IconButton(
                  icon: const Icon(Icons.shopping_cart),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => CartScreen(
                          productsInCart: CartService().items,
                          updateCounter: (_) => setState(_syncWithCart),
                          order: widget.order ?? Order(),
                        ),
                      ),
                    ).then((_) => setState(_syncWithCart));
                  },
                ),
                if (productCounter > 0)
                  Positioned(
                    right: 6,
                    top: 6,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: const BoxDecoration(
                          color: Colors.red, shape: BoxShape.circle),
                      child: Text(
                        "$productCounter",
                        style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 11),
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
        body: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  children: [
                    TextField(
                      controller: _searchController,
                      decoration: InputDecoration(
                        hintText: 'Buscar productos...',
                        prefixIcon: const Icon(Icons.search),
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      onChanged: (value) => setState(() => searchQuery = value),
                    ),
                    const SizedBox(height: 12),
                    Expanded(
                      child: productosFiltrados.isEmpty
                          ? Center(
                              child: Text(
                                "🥬 No hay ofertas disponibles",
                                style: TextStyle(
                                  color: Colors.grey[700],
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                ).merge(fontStyle),
                              ),
                            )
                          : ListView.builder(
                              itemCount: categorias.length,
                              itemBuilder: (context, index) {
                                final categoria = categorias[index];
                                final productosCategoria = productosFiltrados
                                    .where((p) => p.category == categoria)
                                    .toList();

                                return Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Padding(
                                      padding: const EdgeInsets.symmetric(
                                          vertical: 10),
                                      child: Text(
                                        categoria,
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 20,
                                          color: verdePrincipal,
                                        ).merge(fontStyle),
                                      ),
                                    ),
                                    SizedBox(
                                      height: 300,
                                      child: ListView.builder(
                                        physics: const BouncingScrollPhysics(),
                                        scrollDirection: Axis.horizontal,
                                        itemCount: productosCategoria.length,
                                        itemBuilder: (context, i) {
                                          return _buildProductCard(
                                              productosCategoria[i]);
                                        },
                                      ),
                                    ),
                                    const SizedBox(height: 10),
                                  ],
                                );
                              },
                            ),
                    ),
                  ],
                ),
              ),
        bottomNavigationBar: SafeArea(
          child: BottomNavigationBar(
            currentIndex: currentIndex,
            selectedItemColor: Colors.lightGreen.shade900,
            unselectedItemColor: Colors.grey,
            type: BottomNavigationBarType.fixed,
            items: [
              const BottomNavigationBarItem(
                  icon: Icon(Icons.home), label: 'Inicio'),
              if (_userActive)
                const BottomNavigationBarItem(
                    icon: Icon(Icons.shopping_cart), label: 'Pedidos'),
              if (!_userActive)
                const BottomNavigationBarItem(
                    icon: Icon(Icons.person), label: 'Login'),
              if (_userActive)
                const BottomNavigationBarItem(
                    icon: Icon(Icons.person), label: 'Perfil'),
              const BottomNavigationBarItem(
                  icon: Icon(Icons.local_offer), label: 'Descuentos'),
              const BottomNavigationBarItem(
                  icon: Icon(Icons.message_rounded), label: 'WhatsApp'),
            ],
            onTap: _handleNavigation,
          ),
        ),
      ),
    );
  }

  Widget _buildProductCard(Product producto) {
    double originalPrice = producto.priceSale ?? 0.0;
    double finalPrice = producto.finalPrice ?? originalPrice;
    double discountPercent = producto.savingsPct ?? 0.0;

    return Container(
      width: 170,
      margin: const EdgeInsets.only(right: 12, bottom: 10, left: 2),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 6,
            offset: Offset(0, 3),
          )
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Stack(
            children: [
              ClipRRect(
                borderRadius:
                    const BorderRadius.vertical(top: Radius.circular(12)),
                child: Image.network(
                  producto.image ?? '',
                  height: 120,
                  width: 170,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    height: 120,
                    color: Colors.grey.shade200,
                    child: const Icon(Icons.image_not_supported),
                  ),
                ),
              ),
              Positioned(
                right: 6,
                top: 6,
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: const BoxDecoration(
                    color: Colors.yellow,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    "${(discountPercent).toInt()}%",
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                      color: Colors.black,
                    ),
                  ),
                ),
              ),
            ],
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    producto.name ?? 'Producto',
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ).merge(fontStyle),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Antes: \$${NumberFormat('#,###').format(originalPrice)}",
                    style: const TextStyle(
                      decoration: TextDecoration.lineThrough,
                      color: Colors.red,
                      fontSize: 11,
                    ),
                  ),
                  Text(
                    "Ahora: \$${NumberFormat('#,###').format(finalPrice)}",
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: verdePrincipal,
                    ),
                  ),
                ],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(bottom: 12.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  icon: const Icon(Icons.remove_circle, color: Colors.red),
                  onPressed: () => decreaseQuantity(producto),
                ),
                Text(
                  "${producto.quantity ?? 0}",
                  style: const TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 16),
                ),
                IconButton(
                  icon: Icon(Icons.add_circle, color: verdePrincipal),
                  onPressed: () => increaseQuantity(producto),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
