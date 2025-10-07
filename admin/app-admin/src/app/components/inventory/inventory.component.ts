import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { InventoryService } from '../../services/inventory.service';

@Component({
  templateUrl: './inventory.component.html',
  styleUrl: './inventory.component.css'
})
export class InventoryComponent {
  inventories:any = []
  messageInventory = ''
  fechaNewInventory =''
  statusCodeInventory =''
  constructor(
    private router: Router,
    private inventoryService : InventoryService
  ){}
  ngOnInit(): void {
    this.getInventories();
  }
  hasRole(requiredRoles: string[]): boolean {
    return requiredRoles.some(r => localStorage.getItem('role')?.includes(r));
  }
  newInventory(){
    this.inventoryService.createInventory(this.fechaNewInventory).subscribe(
      (res: any) => {
        this.getInventories();
        this.messageInventory = 'Inventario creado exitosamente!';
        this.statusCodeInventory = res.statusCode || '200';
        setTimeout(() => {
          this.messageInventory = '';
        }, 3000);
      },
      (error: any) => {
        this.messageInventory = 'Fallo al crear el Inventario.';
        this.statusCodeInventory = error.status || '500';
        setTimeout(() => {
          this.messageInventory = '';
        }, 3000);
      }
    );
  }
  delete_inventory(id:any){
    this.inventoryService.deleteInventory(id).subscribe(
      (res: any) => {
        this.getInventories();
        this.messageInventory = 'Inventario eliminado exitosamente!';
        this.statusCodeInventory = res.statusCode || '200';
        setTimeout(() => {
          this.messageInventory = '';
        }, 3000);
      },
      (error: any) => {
        this.messageInventory = 'Fallo al eliminar el Inventario.';
        this.statusCodeInventory = error.status || '500';
        setTimeout(() => {
          this.messageInventory = '';
        }, 3000);
      }
    );
  }
  navigateToInventory(id:any){
    this.router.navigate(['/inventory', id]);
  }
  getInventories() {
    this.inventoryService.getInventories().subscribe(
      (res: any) => {
        // Ordenar los inventarios por close_date de mayor a menor
        this.inventories = res.sort((a: any, b: any) => {
          return new Date(b.close_date).getTime() - new Date(a.close_date).getTime();
        });
      }
    );
  }

  productsCost(products: any[]){
    if (products.length === 0) {
      return 0;
    }
    const registeredCount = products.filter(product => product.quantity > 0).length;
    return Math.round(registeredCount);
  }
  productsValue(products: any[]): number {
    if (products.length === 0) {
      return 0;
    }

    // Calcular el valor total multiplicando cantidad y costo, luego sumando
    const totalValue = products.reduce((sum, product) => {
      if (product.quantity > 0 && product.cost > 0) {
        return sum + product.quantity * product.cost;
      }
      return sum;
    }, 0);

    // Retornar el total redondeado
    return Math.round(totalValue);
  }

}
