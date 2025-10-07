import { Component } from '@angular/core';
import { ProductHistoryService } from '../../services/product-history.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-pricing',
  templateUrl: './pricing.component.html',
  styleUrl: './pricing.component.css'
})
export class PricingComponent {
  products: any[] = [];
  filteredProducts: any[] = [];
  searchText: string = '';
  today = new Date();
  yyyy = this.today.getFullYear();
  mm = String(this.today.getMonth() + 1).padStart(2, '0'); // Los meses van de 0 a 11, por eso sumamos 1
  dd = String(this.today.getDate()).padStart(2, '0');
  searchDate_start = `${this.yyyy}-${this.mm}-${this.dd}`;
  searchDate_end = `${this.yyyy}-${this.mm}-${this.dd}`;
  operationDate = `${this.yyyy}-${this.mm}-${this.dd}`;
  product: any = {};
  actionTipo: any = '';
  successMessage: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(private productHistoryService: ProductHistoryService, private router: Router) { }
  ngOnInit(): void {
    this.getProducts(this.searchDate_start,this.searchDate_end);
  }
  getProducts(operation_date_start:any,operation_date_end:any): void {
    this.productHistoryService.getProductsHistory(operation_date_start,operation_date_end)
      .subscribe(products => {
        this.products = products;
        this.filteredProducts = products; // Inicializa la lista de productos filtrados con todos los productos al principio
        this.filterProducts(); // Filtra los productos basados en el texto de búsqueda inicial
      });
  }
  filterProducts(): void {
    const searchText = this.searchText.trim().toLowerCase();

    if (searchText !== '') {
      this.filteredProducts = this.products.filter(product => {
        // Filtra los productos cuyo SKU, nombre o categoría contienen el texto de búsqueda
        return (
          product.sku.toLowerCase().includes(searchText) ||
          product.name.toLowerCase().includes(searchText) ||
          product.category.toLowerCase().includes(searchText)
        );
      });
    } else {
      // Si no hay texto de búsqueda, muestra todos los productos
      this.filteredProducts = this.products;
    }
  }
  updatePrices(operationDate: any): void {
    this.isLoading = true; // Activar el estado de carga
    this.productHistoryService.updatePrices(operationDate).subscribe(
      products => {
        // Procesar la respuesta
        this.successMessage = "Precios actualizados correctamente.";
        this.isLoading = false; // Desactivar el estado de carga
      },
      error => {
        this.errorMessage = "Hubo un error al actualizar los precios.";
        this.isLoading = false; // Desactivar el estado de carga
      }
    );
  }

}
