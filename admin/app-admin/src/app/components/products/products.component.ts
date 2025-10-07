import { Component, OnInit } from '@angular/core';
import { ProductService } from '../../services/product.service';
import { Router } from '@angular/router';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { SupplierService } from '../../services/supplier.service';

@Component({
  selector: 'app-products',
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit {
  products: any[] = [];
  filteredProducts: any[] = [];
  searchText: string = '';
  product: any = {};
  actionTipo: any = '';
  successMessage: string = '';
  errorMessage: string = '';
  sortColumn: string = '';
  sortDirection: number = 1;
  suppliers: any[] = [];
  constructor(private productService: ProductService,
    private router: Router,
      private supplierService : SupplierService
  ) { }

  ngOnInit(): void {
    // Verificar si el usuario está autenticado
    const isLoggedIn = this.checkIfLoggedIn();

    if (!isLoggedIn) {
      // Si no está autenticado, redirigir al usuario a la página de inicio de sesión
      this.router.navigate(['/login']);
    } else {
      // Si está autenticado, cargar los productos
      this.getProducts();
          this.supplierService.getSuppliers().subscribe(
      (res: any) => {
        this.suppliers = res;
      }
    );
    }
  }

  // Función para verificar si el usuario está autenticado (puedes implementar tu propia lógica aquí)
  checkIfLoggedIn(): boolean {
    // Por ejemplo, podrías verificar si existe un token de autenticación en el almacenamiento local
    const token = localStorage.getItem('token');
    return !!token; // Devuelve true si hay un token, de lo contrario false
  }

  getProducts(): void {
    this.productService.getProducts()
      .subscribe(products => {
        this.products = products;
        this.filteredProducts = products; // Inicializa la lista de productos filtrados con todos los productos al principio
        this.filterProducts(); // Filtra los productos basados en el texto de búsqueda inicial
      });
  }
  exportToExcel(descuento = 1): void {
    const exportData = this.products.map(p => ({
      SKU: p.sku,
      Nombre: p.name,
      Precio_Venta: new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(p.price_sale * descuento)
    }));

    const fechaHoy = new Date().toISOString().split('T')[0];
    const worksheet = XLSX.utils.json_to_sheet(exportData);

    // Establecer el ancho de columnas (en caracteres aprox.)
    const wscols = [
      { wch: 20 }, // SKU más ancho
      { wch: 40 }, // Nombre más ancho
      { wch: 20 }  // Precio venta
    ];
    worksheet['!cols'] = wscols;

    const workbook = { Sheets: { 'Productos': worksheet }, SheetNames: ['Productos'] };
    const excelBuffer: any = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });
    saveAs(blob, `productos_${fechaHoy}_FRESCAPP.xlsx`);
  }

  filterProducts(): void {
    if (this.searchText.trim() !== '') {
      const searchTextLower = this.searchText.toLowerCase();

      this.filteredProducts = this.products.filter(product => {
        // Verifica si el texto de búsqueda coincide con alguno de los atributos del producto
        return (
          product.name.toLowerCase().includes(searchTextLower) || // Coincidencia en el nombre
          product.unit?.toLowerCase().includes(searchTextLower) || // Coincidencia en la descripción
          product.category?.toLowerCase().includes(searchTextLower) || // Coincidencia en la categoría
          product.sku?.toLowerCase().includes(searchTextLower) || // Coincidencia en el SKU
          product.child?.toString().includes(searchTextLower) // Coincidencia en el precio
        );
      });
    } else {
      // Si no hay texto de búsqueda, muestra todos los productos
      this.filteredProducts = this.products;
    }
  }

  openEditModal(product: any, tipo: any): void {
    this.product = product;
    this.actionTipo = tipo;
  }

  updated_product(): void {
    // Convierte los campos price_sale, price_purchase, margen, discount y iva_value a tipo decimal
    this.product.price_sale = parseFloat(this.product.price_sale);
    this.product.price_purchase = parseFloat(this.product.price_purchase);
    this.product.margen = parseFloat(this.product.margen);
    this.product.discount = parseFloat(this.product.discount);
    this.product.iva_value = parseFloat(this.product.iva_value);
    this.product.is_visible = Boolean(this.product.is_visible);
    // Convierte el campo iva a tipo boolean
    this.product.iva = this.product.iva === 'true' ? true : false;
    // Llama al servicio para actualizar el producto
    this.productService.updateProduct(this.product.id, this.product).subscribe((data: any) => {
      // Lógica después de actualizar el producto, si es necesario
      this.successMessage = '¡Producto actualizado correctamente!';
      this.getProducts();
      setTimeout(() => {
        this.successMessage = ''; // Reiniciar el mensaje después de unos segundos
      }, 3000); // Mostrar el mensaje durante 3 segundos
    });

  }

  created_product(): void {
    // Convierte los campos price_sale y price_purchase a tipo number
    this.product.price_sale = +this.product.price_sale;
    this.product.price_purchase = +this.product.price_purchase;
    this.product.quantity = 0;
    // Convierte el campo iva a tipo boolean
    this.product.iva = this.product.iva === 'true' ? true : false;
    this.productService.createProduct(this.product).subscribe((data: any) => {
      this.getProducts();
    });

  }
  camposCompletos(): boolean {
    const { name, unit, category, sku, price_sale, price_purchase, discount, margen, iva, iva_value, description, image, status } = this.product;
    return !!name && !!unit && !!category && !!sku && !!price_sale && !!image && !!status;
  }
  updateCataloPage() {
    this.productService.updateCatalogoPage().subscribe((data: any) => {
    });
    }

  sortBy(column: string) {
    if (this.sortColumn === column) {
      this.sortDirection = -this.sortDirection;
    } else {
      this.sortColumn = column;
      this.sortDirection = 1;
    }
    this.filteredProducts.sort((a: any, b: any) => {
      if (a[column] < b[column]) {
        return -1 * this.sortDirection;
      }
      if (a[column] > b[column]) {
        return 1 * this.sortDirection;
      }
      return 0;
    });
  }
}
