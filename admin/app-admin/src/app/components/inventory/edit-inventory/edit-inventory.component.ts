import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { InventoryService } from '../../../services/inventory.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  templateUrl: './edit-inventory.component.html',
  styleUrl: './edit-inventory.component.css'
})
export class EditInventoryComponent {
  inventory:any
  filteredProducts:any = []
  searchTerm: string = '';
  inventoryId = ''
  constructor(
    private router: Router,
    private inventoryService : InventoryService,
    private route: ActivatedRoute,

  ){
    this.route.params.subscribe(params => {
    this.inventoryId = params['id'];
  });

  }
  ngOnInit(): void {
    this.getInventory();
  }
  getInventory() {
    this.inventoryService.getInventory(this.inventoryId).subscribe(
      (res: any) => {
        this.inventory = res;
        this.filteredProducts = this.inventory.products.sort((a:any, b:any) => b.quantity - a.quantity);
      }
    );
  }
  filterProducts() {
    this.filteredProducts = this.inventory.products.filter((product: any) =>
      product.name.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }
  saveChanges(): void {
    // Actualiza los productos en el inventario original solo en los campos 'quantity' y 'cost'
    this.inventory.products = this.inventory.products.map((product:any) => {
      const updatedProduct = this.filteredProducts.find(
        (p:any) => p.sku === product.sku
      );
      if (updatedProduct) {
        return {
          ...product, // Conservar los atributos existentes
          cost: updatedProduct.cost, // Actualizar costo
          quantity: updatedProduct.quantity, // Actualizar cantidad
        };
      }
      return product; // Mantener productos que no estén en filteredProducts
    });

    // Llamada al servicio para actualizar el inventario
    this.inventoryService.updateInventory(this.inventory).subscribe(
      (res: any) => {
        this.getInventory(); // Recarga el inventario actualizado
      },
      (error: any) => {
        console.error('Error al actualizar el inventario:', error);
      }
    );
  }


  // Regresar a la página anterior
  goBack(): void {
    this.router.navigate(['/inventories']); // Ajusta la ruta según tu aplicación
  }
}
