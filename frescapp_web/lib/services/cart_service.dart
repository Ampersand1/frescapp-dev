import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:frescapp/models/product.dart';

class CartItem {
  Product product;
  int quantity;

  CartItem({required this.product, required this.quantity});

  Map<String, dynamic> toJson() => {
        "product": product.toJson(),
        "quantity": quantity,
      };

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      product: Product.fromJson(json["product"]),
      quantity: json["quantity"],
    );
  }
}

class CartService {
  static final CartService _instance = CartService._internal();
  factory CartService() => _instance;
  CartService._internal();

  final Map<String, CartItem> _items = {};

  Map<String, CartItem> get items => _items;

  // ------------------------------
  // 1. AGREGAR PRODUCTO
  // ------------------------------
  void add(Product p) {
    if (_items.containsKey(p.sku)) {
      _items[p.sku]!.quantity += 1;
    } else {
      _items[p.sku!] = CartItem(product: p, quantity: 1);
    }
    saveCart(); 
  }

  // ------------------------------
  // 2. QUITAR PRODUCTO
  // ------------------------------
  void remove(String sku) {
    _items.remove(sku);
    saveCart();
  }

  // ------------------------------
  // 3. LIMPIAR
  // ------------------------------
  void clear() {
    _items.clear();
    saveCart();
  }

  // ------------------------------
  // 4. PERSISTENCIA
  // ------------------------------
  Future<void> saveCart() async {
    final prefs = await SharedPreferences.getInstance();
    final list = _items.values.map((e) => e.toJson()).toList();
    prefs.setString("cart", jsonEncode(list));
  }

  Future<void> loadCart() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString("cart");
    if (raw == null) return;

    List parsed = jsonDecode(raw);
    _items.clear();

    for (var item in parsed) {
      final ci = CartItem.fromJson(item);
      _items[ci.product.sku!] = ci;
    }
  }

  // ------------------------------
  // 5. SINCRONIZAR PRODUCTOS 
  // ------------------------------
  void syncProductData(List<Product> products) {
    for (var p in products) {
      if (_items.containsKey(p.sku)) {
        _items[p.sku]!.product = p;
      }
    }
    saveCart();
  }
}
