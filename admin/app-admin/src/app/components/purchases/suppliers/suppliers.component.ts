import { Component, OnInit } from '@angular/core';
import { SupplierService } from '../../../services/supplier.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-suppliers',
  templateUrl: './suppliers.component.html',
  styleUrls: ['./suppliers.component.css']
})
export class SuppliersComponent implements OnInit {
  suppliers: any[] = [];
  filteredSuppliers: any[] = [];
  searchText: string = '';
  messageSupplier: string = '';
  isEditMode: boolean = false;
  currentSupplier: any = {
    id: null,
    name: '',
    nit: '',
    email: '',
    address: '',
    phone: '',
    nickname: '', // Agregar si es utilizado en el HTML
    typeSupport: ''
  };

  constructor(private supplierService: SupplierService, private router: Router) {}

  ngOnInit(): void {
    this.getSuppliers();
  }

  getSuppliers() {
    this.supplierService.getSuppliers().subscribe(
      (res: any) => {
        this.suppliers = res;
        this.filteredSuppliers = res;
      }
    );
  }

  filterSuppliers() {
    if (this.searchText.trim() !== '') {
      this.filteredSuppliers = this.suppliers.filter(supplier =>
        supplier.name.toLowerCase().includes(this.searchText.toLowerCase()) ||
        supplier.nit.toLowerCase().includes(this.searchText.toLowerCase())
      );
    } else {
      this.filteredSuppliers = this.suppliers;
    }
  }

  setCurrentSupplier(supplier: any) {
    this.isEditMode = true;
    this.currentSupplier = { ...supplier };
  }

  saveSupplier() {
    if (this.isEditMode) {
      this.supplierService.updateSupplier(this.currentSupplier).subscribe(
        (res: any) => {
          this.getSuppliers();
          this.messageSupplier = 'Proveedor actualizado exitosamente!';
          this.clearMessageAfterDelay();
        },
        (error: any) => {
          this.messageSupplier = 'Error al actualizar el proveedor.';
          this.clearMessageAfterDelay();
        }
      );
    } else {
      this.supplierService.createSupplier(this.currentSupplier).subscribe(
        (res: any) => {
          this.getSuppliers();
          this.messageSupplier = 'Proveedor creado exitosamente!';
          this.clearMessageAfterDelay();
        },
        (error: any) => {
          this.messageSupplier = 'Error al crear el proveedor.';
          this.clearMessageAfterDelay();
        }
      );
    }
    this.isEditMode = false;
    this.resetCurrentSupplier();
  }

  deleteSupplier(supplierId: number) {
    this.supplierService.deleteSupplier(supplierId).subscribe(
      (res: any) => {
        this.getSuppliers();
        this.messageSupplier = 'Proveedor eliminado exitosamente!';
        this.clearMessageAfterDelay();
      },
      (error: any) => {
        this.messageSupplier = 'Error al eliminar el proveedor.';
        this.clearMessageAfterDelay();
      }
    );
  }

  resetCurrentSupplier() {
    this.currentSupplier = { id: null, name: '', nit: '', email: '', address: '', phone: '', nickname: '', typeSupport: '' };
  }

  clearMessageAfterDelay() {
    setTimeout(() => {
      this.messageSupplier = '';
    }, 3000);
  }
}
