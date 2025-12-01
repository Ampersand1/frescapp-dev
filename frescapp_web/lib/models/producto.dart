class Producto {
  final String nombre;
  final String categoria;
  final double precio;
  final double descuento;
  final String imagen;

  Producto({
    required this.nombre,
    required this.categoria,
    required this.precio,
    required this.descuento,
    required this.imagen,
  });

  double get precioFinal => precio - (precio * descuento / 100);

  bool get tieneDescuento => descuento > 0;
}
