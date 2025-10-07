import { Component, OnInit } from '@angular/core';
import { ClientesService } from '../../services/clientes.service';
import { OrderService } from '../../services/order.service';

@Component({
  selector: 'app-clientes',
  templateUrl: './clientes.component.html',
  styleUrls: ['./clientes.component.css']
})
export class ClientesComponent implements OnInit {
  customers: any[] = [];
  filteredCustomers: any[] = [];
  searchText: string = '';
  selectedCustomer: any = {};
  isNewCustomer: boolean = true;
  documentTypes: string[] = [];
  cateroryTypes: string[] = [];
  statusTypes : string[] = [];
  roles : string[] = ['Administrador','Comercial','Comprador','Cliente']
  userPassword = {
    newPassword: '',
    confirmPassword: ''
  };
  passwordMismatch = false;

  constructor(
              private clientesService: ClientesService,
              private orderService: OrderService  ) {}

  ngOnInit(): void {
    this.getClientes();
    this.orderService.getConfig().subscribe(config => {
      this.documentTypes = config.document_type;
      this.cateroryTypes = config.category;
      this.statusTypes = ['active','inactive']
    });
  }

  getClientes() {
    this.clientesService.getClientes().subscribe(
      (data) => {
        this.customers = data;
        this.filteredCustomers = this.customers;
      },
      (error) => {
        console.error('Error al obtener clientes:', error);
        // Manejo de errores
      }
    );
  }

  filterCustomers() {
    this.filteredCustomers = this.customers.filter(customer =>
      customer.name.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.phone.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.document.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.email.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.restaurant_name.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.status.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  openEditModal(customer: any, type: string): void {
    this.selectedCustomer = type === 'new' ? {} : { ...customer };
    if (type == 'edit'){
      this.isNewCustomer = false;
    }else{
      this.isNewCustomer = true;
    }
  }

  edit_customer(customer: any) {
    this.openEditModal(customer, 'edit');
  }

  saveCustomer() {
    this.clientesService.updateCliente(this.selectedCustomer).subscribe(
      (data) => {
        this.getClientes();
      },
      (error) => {
        console.error('Error al actualizar cliente:', error);
        // Manejo de errores
      }
    );
  }
  createCustomer() {
    this.clientesService.createCliente(this.selectedCustomer).subscribe(
      (data) => {
        this.getClientes();
      },
      (error) => {
        console.error('Error al actualizar cliente:', error);
        // Manejo de errores
      }
    );
  }

  addProduct() {
    this.selectedCustomer.list_products.push(''); // Añade un producto vacío (string)
  }

  // Método para eliminar un producto del arreglo
  removeProduct(index: number) {
    this.selectedCustomer.list_products.splice(index, 1); // Elimina el producto en el índice indicado
  }
  trackByIndex(index: number, item: any): any {
    return index;
  }
  delete_customer(customer: any) {
    if (confirm('¿Está seguro de que desea eliminar este cliente?')) {
      this.clientesService.deleteCliente(customer._id).subscribe(
        () => {
          this.customers = this.customers.filter(c => c._id !== customer._id);
          this.filterCustomers();
        },
        (error) => {
          console.error('Error al eliminar cliente:', error);
        }
      );
    }
  }
  checkPasswordMismatch() {
    this.passwordMismatch = this.userPassword.newPassword !== this.userPassword.confirmPassword;
  }
  changePassword(){
    this.checkPasswordMismatch();
    if (!this.passwordMismatch) {
      this.clientesService.changePassword(this.selectedCustomer.id,this.userPassword.newPassword).subscribe(
        () => {

        },
        (error) => {
          console.error('Error al cambiar la contraseña:', error);
        }
      );
    }
  }
}
