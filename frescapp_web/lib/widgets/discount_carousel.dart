import 'package:flutter/material.dart';
import '../models/producto.dart';
import 'product_card.dart';

class DiscountCarousel extends StatelessWidget {
  final String categoria;
  final List<Producto> productos;

  const DiscountCarousel({Key? key, required this.categoria, required this.productos}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (productos.isEmpty) return SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Text(
            categoria,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ),
        SizedBox(
          height: 210,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: productos.length,
            itemBuilder: (context, index) {
              return ProductCard(producto: productos[index]);
            },
          ),
        ),
      ],
    );
  }
}
