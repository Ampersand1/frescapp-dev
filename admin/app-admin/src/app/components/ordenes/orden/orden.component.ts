import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ClientesService } from '../../../services/clientes.service';
import { OrderService } from '../../../services/order.service';

@Component({
  selector: 'app-orden',
  templateUrl: './orden.component.html',
  styleUrl: './orden.component.css'
})
export class OrdenComponent implements OnInit {
  constructor(private route: ActivatedRoute
        ,private clienteService: ClientesService
        ,private orderService: OrderService

  ) {}

  ngOnInit(): void {
    this.orderNumber = this.route.snapshot.paramMap.get('id') ?? '';
    this.isNuevo = this.orderNumber === 'new';
    this.getCustomers();
    // Simula que se carga una orden si no es nueva
    if (!this.isNuevo) {
      // Aquí deberías llamar tu servicio real
      this.order = {
        order_number: this.orderNumber,
        customer_name: 'Cliente Ejemplo',
        // ...otros campos
      };
    }
  }

  // ---------------- PROPIEDADES ----------------

  // Modo de operación de la orden
// Modo actual: 'manual' | 'formato' | 'whatsapp'
  modo: string = 'manual';
  showHeaderOrder: boolean = true;
  orderNumber: string = '';
  isNuevo: boolean = false;
  selectedFile: File | null = null;
  // Datos de la orden
  order: any = {
    order_number: '',
    customer_email: '',
    customer_name: '',
    customer_documentType: '',
    customer_documentNumber: '',
    customer_phone: '',
    total: 0,
    delivery_date: '',
    deliverySlot: '',
    paymentMethod: '',
    payment_date: '',
    deliveryAddress: '',
    deliveryAddressDetails: '',
    status: '',
    seller_name: '',
    source: '',
    driver_name: '',
    products: []
  };

  // Listas de opciones
  customers: any[] = []; // Debes llenar esto con tus clientes
  products: any[] = []; // Lista de productos
  documentTypes: string[] = ['CC', 'NIT', 'CE'];
  deliverySlots: string[] = ['Mañana', 'Tarde'];
  paymentMethods: string[] = ['Efectivo', 'Transferencia', 'Tarjeta'];
  statusOrders: string[] = ['Pendiente', 'Pagada', 'Cancelada'];
  seller: string[] = ['Vendedor 1', 'Vendedor 2'];
  source: string[] = ['App', 'Llamada', 'Web'];
  driver: string[] = ['Conductor A', 'Conductor B'];

  // Cliente seleccionado
  selectedCustomerId: any;

  // Texto WhatsApp
  mensajeWhatsapp: string = '';

  // ---------------- MÉTODOS ----------------

  toggleHeaderOrder() {
    this.showHeaderOrder = !this.showHeaderOrder;
  }

  onCustomerSelect() {
    // Lógica al seleccionar cliente
    console.log('Cliente seleccionado:', this.selectedCustomerId);
  }

  onProductSelect(product: any) {
    // Aquí puedes llenar más info del producto
    console.log('Producto actualizado:', product);
  }

  addProduct() {
    this.order.products.push({
      id: null,
      name: '',
      sku: '',
      price_sale: 0,
      quantity: 1,
      iva: false,
      iva_value: 0
    });
  }

  removeProduct(product: any) {
    this.order.products = this.order.products.filter((p: any) => p !== product);
  }

  camposCompletos(): boolean {
    // Validación simple (puedes personalizarla más)
    return this.order.customer_name && this.order.delivery_date && this.order.products.length > 0;
  }

  saveOrder() {
    console.log('Orden guardada:', this.order);
  }

  enviarWhatsapp() {
    console.log('Mensaje WhatsApp:', this.mensajeWhatsapp);
    // Aquí conectarías con tu integración ChatGPT-WhatsApp
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      // Puedes parsear el CSV aquí o usar un servicio
    }
  }

  procesarArchivo() {
    console.log('Procesando archivo para cliente:', this.selectedCustomerId);
    console.log(this.order);
    this.orderService.createOrderFromFile(this.selectedFile, this.order)
      .subscribe(response => {
        console.log('Orden creada desde archivo:', response);
      }, error => {
        console.error('Error al crear orden desde archivo:', error);
      });
  }
  getCustomers() {
  this.clienteService.getClientes()
    .subscribe(customers => {
      this.customers = customers.map(c => ({
        ...c,
        customLabel: `${c.name} (${c.address || 'sin dirección'})`
      }));
    });
}
}
