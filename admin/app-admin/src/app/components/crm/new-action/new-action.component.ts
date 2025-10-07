import { Component, OnInit } from '@angular/core';
import { ActionService } from '../../../services/action.service';
import { Router } from '@angular/router';
import { ClientesService } from '../../../services/clientes.service';
import { OrderService } from '../../../services/order.service';

@Component({
  selector: 'app-new-action',
  templateUrl: './new-action.component.html',
  styleUrls: ['./new-action.component.css']
})
export class NewActionComponent implements OnInit {
  newActionObject: any = {
    dateAction: '',
    dateSolution: '',
    type: {},
    customer: {},
    orderNumber: '',
    manager: '',
    status: 'Creada',
    actionComment : '',
    solutionType : '',
    solutionComment:'',
    longituted:'',
    latituted:''
  };

  customers: any[] = [];
  actionTypes: any[] = [];
  orders: any[] = [];
  managers: string[] = [];
  searchText: string = '';
  isCustomerExisting: boolean = true;

  constructor(
    private actionService: ActionService,
    private customerService: ClientesService,
    private orderService: OrderService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadCustomers();
    this.orderService.getConfig().subscribe(
      (data) => {
        this.actionTypes = data.actionsType;
        this.managers = data.comercials;
      }
    )
  }

  loadCustomers() {
    this.customerService.getClientes().subscribe(
      (data) => {
        this.customers = data;
      },
      (error) => {
        console.error('Error al cargar los clientes:', error);
      }
    );
  }

  loadOrders(customerEmail: string) {
    this.orderService.getLastOrdersByCustomerId(customerEmail).subscribe(
      (data) => {
        this.orders = data;
      },
      (error) => {
        console.error('Error al cargar los pedidos:', error);
      }
    );
  }

  selectCustomer(customer: any) {
    this.newActionObject.customer = customer;
    this.loadOrders(customer.email);
  }

  onTypeChange() {
    if (this.newActionObject.type.requiresOrder  && this.newActionObject.customer.id) {
      this.loadOrders(this.newActionObject.customer.email);
    }
  }


  createAction() {
    if (!this.newActionObject.dateAction || !this.newActionObject.type) {
      alert('Por favor, completa todos los campos obligatorios.');
      return;
    }

    this.actionService.createAction(this.newActionObject).subscribe(
      (response) => {
        this.router.navigate(['/crm']); // Navegar a la lista de acciones después de crear la acción
      },
      (error) => {
        console.error('Error al crear la acción:', error);
      }
    );
  }
  filteredCustomers(): any[] {
    if (!this.searchText) {
      return this.customers;
    }
    const lowerSearchText = this.searchText.toLowerCase();
    return this.customers.filter(customer =>
      customer.phone.toLowerCase().includes(lowerSearchText) ||
      customer.name.toLowerCase().includes(lowerSearchText) ||
      customer.email.toLowerCase().includes(lowerSearchText)
    );
  }
  backList(){
    this.router.navigate(['/crm'])
  }
  onCustomerExistsChange(): void {
    if (!this.isCustomerExisting) {
      this.newActionObject.customer =   {
        "address": "",
        "category": "",
        "document": "",
        "document_type": "",
        "email": "",
        "latitude": "",
        "longitude": "",
        "micro_category": "",
        "name": "Cliente no existe",
        "phone": ""
      }
    }
  }
}
