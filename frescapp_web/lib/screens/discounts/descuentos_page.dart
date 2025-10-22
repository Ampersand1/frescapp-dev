import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:frescapp/models/product.dart';
import 'package:frescapp/services/product_service.dart'; // Asegúrate de que la ruta sea correcta

class DescuentosPage extends StatefulWidget {
  const DescuentosPage({super.key});

  @override
  State<DescuentosPage> createState() => _DescuentosPageState();
}

class _DescuentosPageState extends State<DescuentosPage> {
  final TextEditingController _searchController = TextEditingController();
  final ProductService productService = ProductService();

  String searchQuery = '';
  late Future<List<Product>> productosFuture;

  final Color verdePrincipal = const Color(0xFF5E6B4E);
  final Color fondo = const Color(0xFFF8F8E8);

  @override
  void initState() {
    super.initState();
    productosFuture = productService.getDiscountedProducts();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: fondo,
      appBar: AppBar(
        title: const Text(
          'PromFres',
          style: TextStyle(fontFamily: 'Poppins'),
        ),
        backgroundColor: verdePrincipal,
        foregroundColor: Colors.white,
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            // barra de busqueda
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Buscar productos...',
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onChanged: (value) {
                setState(() => searchQuery = value);
              },
            ),
            const SizedBox(height: 12),

            // para despues (OJO)
            Expanded(
              child: FutureBuilder<List<Product>>(
                future: productosFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(
                      child: CircularProgressIndicator(),
                    );
                  } else if (snapshot.hasError) {
                    return Center(
                      child: Text(
                        'Error al cargar descuentos:\n${snapshot.error}',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.red),
                      ),
                    );
                  } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                    return const Center(
                      child: Text('No hay descuentos disponibles'),
                    );
                  }

                  // filtrar productos 
                  final productosFiltrados = snapshot.data!
                      .where((p) => (p.name ?? '')
                          .toLowerCase()
                          .contains(searchQuery.toLowerCase()))
                      .toList();

                  final categorias = productosFiltrados
                      .map((p) => p.category ?? '')
                      .toSet()
                      .toList();

                  // carruseles
                  return ListView.builder(
                    itemCount: categorias.length,
                    itemBuilder: (context, index) {
                      final categoria = categorias[index];
                      final productosCategoria = productosFiltrados
                          .where((p) => p.category == categoria)
                          .toList();

                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // diferentes categorías 
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 8.0),
                            child: Text(
                              categoria,
                              style: TextStyle(
                                fontFamily: 'Poppins',
                                fontWeight: FontWeight.bold,
                                fontSize: 18,
                                color: verdePrincipal,
                              ),
                            ),
                          ),

                          // intento carrusel 
                          SizedBox(
                            height: 250,
                            child: ListView.builder(
                              scrollDirection: Axis.horizontal,
                              physics: const BouncingScrollPhysics(),
                              itemCount: productosCategoria.length,
                              itemBuilder: (context, i) {
                                final producto = productosCategoria[i];
                                final precioDescuento = producto.priceSale !=
                                        null
                                    ? producto.priceSale! *
                                        (1 - (producto.discount ?? 0) / 100)
                                    : 0.0;
                                bool isHovered = false;

                                return StatefulBuilder(
                                  builder: (context, setStateCard) {
                                    return MouseRegion(
                                      onEnter: (_) =>
                                          setStateCard(() => isHovered = true),
                                      onExit: (_) =>
                                          setStateCard(() => isHovered = false),
                                      child: AnimatedContainer(
                                        duration:
                                            const Duration(milliseconds: 200),
                                        width: 170,
                                        margin:
                                            const EdgeInsets.only(right: 12),
                                        decoration: BoxDecoration(
                                          color: isHovered
                                              ? Colors.grey.shade200
                                              : Colors.white,
                                          borderRadius:
                                              BorderRadius.circular(12),
                                          boxShadow: [
                                            if (isHovered)
                                              const BoxShadow(
                                                color: Colors.black26,
                                                blurRadius: 8,
                                                offset: Offset(0, 4),
                                              ),
                                          ],
                                        ),
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.stretch,
                                          children: [
                                            ClipRRect(
                                              borderRadius:
                                                  const BorderRadius.vertical(
                                                      top:
                                                          Radius.circular(12)),
                                              child: Image.network(
                                                producto.image ??
                                                    'https://via.placeholder.com/150',
                                                height: 110,
                                                fit: BoxFit.cover,
                                                errorBuilder: (context, error,
                                                    stackTrace) {
                                                  return Container(
                                                    height: 110,
                                                    color: Colors.grey.shade100,
                                                    child: const Icon(
                                                      Icons.image_not_supported,
                                                      size: 40,
                                                      color: Colors.grey,
                                                    ),
                                                  );
                                                },
                                              ),
                                            ),
                                            Padding(
                                              padding:
                                                  const EdgeInsets.all(6.0),
                                              child: Column(
                                                children: [
                                                  Text(
                                                    producto.name ?? '',
                                                    style: const TextStyle(
                                                      fontFamily: 'Poppins',
                                                      fontWeight:
                                                          FontWeight.bold,
                                                      fontSize: 13,
                                                    ),
                                                    textAlign: TextAlign.center,
                                                    maxLines: 2,
                                                    overflow:
                                                        TextOverflow.ellipsis,
                                                  ),
                                                  Text(
                                                    'Antes: \$${NumberFormat('#,###').format(producto.priceSale ?? 0)}',
                                                    style: const TextStyle(
                                                      decoration: TextDecoration
                                                          .lineThrough,
                                                      color: Colors.red,
                                                      fontSize: 11.5,
                                                    ),
                                                  ),
                                                  Text(
                                                    'Ahora: \$${NumberFormat('#,###').format(precioDescuento)}',
                                                    style: TextStyle(
                                                      fontFamily: 'Poppins',
                                                      fontWeight:
                                                          FontWeight.bold,
                                                      color: verdePrincipal,
                                                      fontSize: 13.5,
                                                    ),
                                                  ),
                                                  const SizedBox(height: 4),
                                                  Row(
                                                    mainAxisAlignment:
                                                        MainAxisAlignment
                                                            .center,
                                                    children: [
                                                      IconButton(
                                                        icon: const Icon(
                                                          Icons.remove_circle,
                                                          color:
                                                              Colors.redAccent,
                                                        ),
                                                        onPressed: () {
                                                          setState(() {
                                                            if ((producto.quantity ??
                                                                    0) >
                                                                0) {
                                                              producto.quantity =
                                                                  (producto.quantity ??
                                                                          0) -
                                                                      1;
                                                            }
                                                          });
                                                        },
                                                      ),
                                                      Text(
                                                        '${producto.quantity?.toInt() ?? 0}',
                                                        style: const TextStyle(
                                                          fontSize: 14,
                                                          fontFamily: 'Poppins',
                                                        ),
                                                      ),
                                                      IconButton(
                                                        icon: Icon(
                                                          Icons.add_circle,
                                                          color:
                                                              verdePrincipal,
                                                        ),
                                                        onPressed: () {
                                                          setState(() {
                                                            producto.quantity =
                                                                (producto.quantity ??
                                                                        0) +
                                                                    1;
                                                          });
                                                        },
                                                      ),
                                                    ],
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  },
                                );
                              },
                            ),
                          ),
                          const SizedBox(height: 20),
                        ],
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
