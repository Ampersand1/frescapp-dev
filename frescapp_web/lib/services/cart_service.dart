import 'package:frescapp/models/product.dart';

class CartService {
  static final CartService _instance = CartService._internal();
  factory CartService() => _instance;
  CartService._internal();

  // Map SKU -> cantidad (fuente de la verdad)
  final Map<String, int> _quantities = {};

  // Map SKU -> snapshot de Product (último conocido para mostrar en UI)
  final Map<String, Product> _productSnapshots = {};

  // Seguridad: devuelve sku no-nula o lanza
  String _safeSku(Product p) {
    if (p.sku == null || p.sku!.isEmpty) {
      throw Exception("Producto sin SKU válido en CartService");
    }
    return p.sku!;
  }

  // Devuelve lista de Product (snapshots) con quantity asignada desde _quantities
  List<Product> get items {
    List<Product> out = [];
    _quantities.forEach((sku, qty) {
      final snapshot = _productSnapshots[sku];
      if (snapshot != null) {
        // clona o crea copia mínima para no exponer mutación directa si lo prefieres
        final p = Product.fromJson(snapshot.toJson());
        p.quantity = qty;
        out.add(p);
      } else {
        // si no hay snapshot, creamos un product mínimo para UI
        out.add(Product(sku: sku, quantity: qty));
      }
    });
    return out;
  }

  // Si existe snapshot, actualiza sus campos relevantes; si no existe, crea uno
  void _ensureSnapshot(Product p) {
    final sku = _safeSku(p);
    final existing = _productSnapshots[sku];
    if (existing == null) {
      // Guardamos una copia para evitar aliasing con el objeto que pasa UI
      _productSnapshots[sku] = Product.fromJson(p.toJson());
    } else {
      // Actualizamos campos importantes (precio, finalPrice, name, image, hasDiscount, savingsPct)
      existing.name = p.name ?? existing.name;
      existing.priceSale = p.priceSale ?? existing.priceSale;
      existing.finalPrice = p.finalPrice ?? existing.finalPrice;
      existing.hasDiscount = p.hasDiscount || existing.hasDiscount;
      existing.savingsPct = p.savingsPct ?? existing.savingsPct;
      existing.image = p.image ?? existing.image;
    }
  }

  void addProduct(Product product) {
    final sku = _safeSku(product);
    _ensureSnapshot(product);
    _quantities[sku] = (_quantities[sku] ?? 0) + 1;
  }

  void removeProduct(Product product) {
    final sku = _safeSku(product);
    final current = _quantities[sku] ?? 0;
    if (current <= 1) {
      _quantities.remove(sku);
      _productSnapshots.remove(sku); // opcional: si quieres mantener snapshot, quita esta línea
    } else {
      _quantities[sku] = current - 1;
    }
  }

  void setQuantity(Product product, int qty) {
    final sku = _safeSku(product);
    if (qty <= 0) {
      _quantities.remove(sku);
      _productSnapshots.remove(sku); // opcional
    } else {
      _ensureSnapshot(product);
      _quantities[sku] = qty;
    }
  }

  double get total {
    double sum = 0;
    for (var entry in _quantities.entries) {
      final sku = entry.key;
      final qty = entry.value;
      final p = _productSnapshots[sku];
      final original = p?.priceSale ?? 0;
      final finalPrice = p?.finalPrice ?? original;
      sum += finalPrice * qty;
    }
    return sum;
  }

  double get savings {
    double sum = 0;
    for (var entry in _quantities.entries) {
      final sku = entry.key;
      final qty = entry.value;
      final p = _productSnapshots[sku];
      if (p == null) continue;
      final original = p.priceSale ?? 0;
      final finalPrice = p.finalPrice ?? original;
      if (p.hasDiscount == true) {
        sum += (original - finalPrice) * qty;
      }
    }
    return sum;
  }

  void clear() {
    _quantities.clear();
    _productSnapshots.clear();
  }

  // Helper: cantidad por sku
  int qtyForSku(String sku) => _quantities[sku] ?? 0;

  // Actualiza snapshot (útil si al recargar productos quieres refrescar los snapshots)
  void updateSnapshotFromProduct(Product p) {
    _safeSku(p);
    _ensureSnapshot(p);
  }
}
