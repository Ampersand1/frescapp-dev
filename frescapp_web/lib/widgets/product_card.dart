import 'package:flutter/material.dart';
import '../models/producto.dart';

class ProductCard extends StatelessWidget {
  final Producto producto;

  const ProductCard({Key? key, required this.producto}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 160,
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 3)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            child: Image.network(producto.imagen, height: 100, width: double.infinity, fit: BoxFit.cover),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(producto.nombre, style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                if (producto.tieneDescuento) ...[
                  Text(
                    '\$${producto.precio.toStringAsFixed(2)}',
                    style: const TextStyle(decoration: TextDecoration.lineThrough, color: Colors.grey, fontSize: 12),
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '\$${producto.precioFinal.toStringAsFixed(2)}',
                        style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.redAccent,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          '-${producto.descuento.toStringAsFixed(0)}%',
                          style: const TextStyle(color: Colors.white, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ] else ...[
                  Text('\$${producto.precio.toStringAsFixed(2)}',
                      style: const TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
