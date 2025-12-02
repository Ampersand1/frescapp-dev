import 'package:frescapp/models/product.dart';
import 'package:frescapp/models/order.dart';

/// Sincroniza las cantidades de los productos de la lista visual (allProducts)
/// con las cantidades guardadas en la orden que viaja entre pantallas.
void syncProducts(List<Product> allProducts, Order order) {
  if (order.products == null) return;

  for (var product in allProducts) {
    var match = order.products!.firstWhere(
      (p) => p.sku == product.sku,
      orElse: () => Product(sku: "dummy"),
    );

    if (match.sku != "dummy") {
      product.quantity = match.quantity;
    } else {
      product.quantity = 0;
    }
  }
}

/// Combina la UI actual (allProducts) con la orden antes de navegación.
/// Limpia los productos en 0 y deja solo los válidos.
Order syncOrderProducts(List<Product> allProducts, Order order) {
  order.products = allProducts
      .where((p) => (p.quantity ?? 0) > 0)
      .map((p) => Product(
            sku: p.sku,
            name: p.name,
            category: p.category,
            priceSale: p.priceSale,
            finalPrice: p.finalPrice,
            quantity: p.quantity,
            image: p.image,
            hasDiscount: p.hasDiscount,
            savingsPct: p.savingsPct,
          ))
      .toList();

  return order;
}
