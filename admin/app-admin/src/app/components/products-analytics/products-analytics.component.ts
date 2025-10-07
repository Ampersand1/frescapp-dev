import { Component, OnInit } from '@angular/core';
import { ProductsAnalyticsService } from '../../services/products-analytics.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-products-analytics',
  templateUrl: './products-analytics.component.html',
  styleUrl: './products-analytics.component.css'
})
export class ProductsAnalyticsComponent implements OnInit {
  constructor(private productService: ProductsAnalyticsService, private router: Router) { }
  products: any[] = [];
  filteredProducts: any[] = [];
  searchText: string = '';
  sortColumn: string = '';
  sortDirection: number = 1;
  ngOnInit(): void {
    this.getProducts();
  }
  getProducts(): void {
    this.productService.getProducts()
      .subscribe(products => {
        this.products = products;
        this.filteredProducts = products; // Inicializa la lista de productos filtrados con todos los productos al principio
        this.filterProducts(); // Filtra los productos basados en el texto de búsqueda inicial
      });
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
