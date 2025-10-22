import 'package:flutter/material.dart';

class DescuentosPage extends StatelessWidget {
  final List<Map<String, dynamic>> ofertas = [
    {
      'nombre': 'Tomate',
      'imagen': 'assets/products/BOG-CAT001-00001.png',
      'precioOriginal': 5895,
      'precioDescuento': 5300,
      'descuento': 10,
      'categoria': 'Frutas'
    },
    {
      'nombre': 'Perejil Liso Atado',
      'imagen': 'assets/images/BOG-CAT004-00001.png',
      'precioOriginal': 7448,
      'precioDescuento': 6700,
      'descuento': 10,
      'categoria': 'Hortalizas'
    },
    {
      'nombre': 'Yuca Tamaño Mixto',
      'imagen': 'assets/images/yuca.png',
      'precioOriginal': 4200,
      'precioDescuento': 3900,
      'descuento': 7,
      'categoria': 'Tubérculos'
    },
    {
      'nombre': 'Cebolla Roja Cabeza',
      'imagen': 'assets/images/cebolla_roja.png',
      'precioOriginal': 3390,
      'precioDescuento': 3200,
      'descuento': 5,
      'categoria': 'Verduras'
    },
  ];

  final List<Map<String, dynamic>> categorias = [
    {'nombre': 'Verduras', 'icono': Icons.eco},
    {'nombre': 'Frutas', 'icono': Icons.apple},
    {'nombre': 'Tubérculos', 'icono': Icons.yard},
    {'nombre': 'Hortalizas', 'icono': Icons.local_florist},
    {'nombre': 'Abarrotes', 'icono': Icons.shopping_bag},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF9F9E8),
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: const Text(
          'Ofertas',
          style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        elevation: 1,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "Ofertas destacadas",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              SizedBox(
                height: 190,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: ofertas.length,
                  itemBuilder: (context, index) {
                    final oferta = ofertas[index];
                    return _OfertaCard(oferta: oferta);
                  },
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                "Busca por categoría",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              SizedBox(
                height: 90,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: categorias.length,
                  itemBuilder: (context, index) {
                    final cat = categorias[index];
                    return Padding(
                      padding: const EdgeInsets.only(right: 12),
                      child: Column(
                        children: [
                          CircleAvatar(
                            radius: 28,
                            backgroundColor: Colors.green.shade100,
                            child: Icon(cat['icono'], color: Colors.green),
                          ),
                          const SizedBox(height: 6),
                          Text(cat['nombre'], style: const TextStyle(fontSize: 12))
                        ],
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                "Súper descuentos",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              Column(
                children: ofertas.map((o) => _DescuentoItem(oferta: o)).toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OfertaCard extends StatelessWidget {
  final Map<String, dynamic> oferta;

  const _OfertaCard({required this.oferta});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 160,
      margin: const EdgeInsets.only(right: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
              color: Colors.grey.shade300, blurRadius: 6, offset: const Offset(2, 2))
        ],
      ),
      child: Stack(
        children: [
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 10),
              Image.asset(oferta['imagen'], height: 70),
              const SizedBox(height: 8),
              Text(
                oferta['nombre'],
                textAlign: TextAlign.center,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 4),
              Text(
                "Antes: \$${oferta['precioOriginal']}",
                style: const TextStyle(
                    decoration: TextDecoration.lineThrough, color: Colors.grey),
              ),
              Text(
                "\$${oferta['precioDescuento']}",
                style: const TextStyle(
                    color: Colors.green, fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ],
          ),
          Positioned(
            top: 6,
            left: 6,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                  color: Colors.yellow.shade700,
                  borderRadius: BorderRadius.circular(8)),
              child: Text(
                "-${oferta['descuento']}%",
                style: const TextStyle(
                    fontWeight: FontWeight.bold, color: Colors.black, fontSize: 12),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _DescuentoItem extends StatelessWidget {
  final Map<String, dynamic> oferta;

  const _DescuentoItem({required this.oferta});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
              color: Colors.grey.shade300, blurRadius: 6, offset: const Offset(2, 2))
        ],
      ),
      child: Row(
        children: [
          Image.asset(oferta['imagen'], height: 60),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(oferta['nombre'],
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 14)),
                Text(oferta['categoria'],
                    style: const TextStyle(color: Colors.grey, fontSize: 12)),
                Row(
                  children: [
                    Text(
                      "\$${oferta['precioDescuento']}",
                      style: const TextStyle(
                          color: Colors.yellow,
                          fontSize: 16,
                          fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      "\$${oferta['precioOriginal']}",
                      style: const TextStyle(
                          decoration: TextDecoration.lineThrough,
                          color: Colors.grey),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const Icon(Icons.add_circle, color: Colors.green),
        ],
      ),
    );
  }
}
