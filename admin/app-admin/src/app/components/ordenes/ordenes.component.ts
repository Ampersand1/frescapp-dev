import { Component,  OnInit } from '@angular/core';
import { OrderService } from '../../services/order.service';
import { Router } from '@angular/router';
import { RoutesService } from '../../services/routes.service';
import { ProductService } from '../../services/product.service';
import { ClientesService } from '../../services/clientes.service';
import { DomSanitizer } from '@angular/platform-browser';
import { AlegraService } from '../../services/alegra.service';
import { DatePipe } from '@angular/common';
import { WooService } from '../../services/woo.service';

@Component({
  selector: 'app-orders',
  templateUrl: './ordenes.component.html',
  styleUrls: ['./ordenes.component.css']
})
export class OrdenesComponent implements OnInit {
  orders: any[] | [] | undefined;
  filteredOrders: any[] | undefined;
  searchText: string = '';
  today = new Date();
  yyyy = this.today.getFullYear();
  mm = String(this.today.getMonth() + 1).padStart(2, '0'); // Los meses van de 0 a 11, por eso sumamos 1
  dd = String(this.today.getDate()).padStart(2, '0');
  searchDate_start = `${this.yyyy}-${this.mm}-${this.dd}`;
  searchDate_end = `${this.yyyy}-${this.mm}-${this.dd}`;
  searchDate = `${this.yyyy}-${this.mm}-${this.dd}`;
  searchStartDate = `${this.yyyy}-${this.mm}-${this.dd}`;
  searchEndDate = `${this.yyyy}-${this.mm}-${this.dd}`;
  searchStatus = 'Estado'
  statusOrders: string[] = ['Estado','Creada','Por entregar','Pagada','Pendiente de pago'];
  source : string[] = ['Página','Aplicación','Web'];
  driver : string[] = ['Carlos','Diago', 'Jhony','Sebas','Cata']
  seller : string[] = ['Cata','Diago','Migue','Auto'];
  order: any = {};
  product: any = {};
  customers: any[]  = [];
  selectedCustomerId: number | undefined;
  actionType: any = '';
  successMessage: string = '';
  failedMessage: any = '';
  documentTypes: string[] = [];
  paymentMethods: string[] = [];
  deliverySlots: string[] = [];
  products: any[] = [];
  selectedProductId: number | undefined;
  selectedsku: string = '';
  pdfData: any;
  facturaData: any;
  messageAlegra = '';
  statusCodeAlegra = '';
  sortColumn: string = '';
  sortDirection: string = 'asc';
  orderNumbertosync :string = '';
  order_numer_sug:string = Math.floor(10000 + Math.random() * 90000).toString();
  evidence:any = '';
  titleEvidence:any = '';
  typeEvidence:any = '';
  showHeaderOrder: boolean = true;
  institucion: boolean = false;
  constructor(
    private orderService: OrderService
    ,private router: Router
    ,private productService: ProductService
    ,private clienteService: ClientesService
    ,private sanitizer: DomSanitizer
    ,private alegraService: AlegraService
    ,private datePipe: DatePipe
    ,private wooService: WooService
    ,private routeService : RoutesService
  ) { }

  ngOnInit(): void {
    const isLoggedIn = this.checkIfLoggedIn();

    if (!isLoggedIn) {
      this.router.navigate(['/login']);
    } else {
      this.getOrders('date');
      this.orderService.getConfig().subscribe(config => {
        this.documentTypes = config.document_type;
        this.paymentMethods = config.payments_method;
        this.deliverySlots = config.delivery_slots;
      });
      this.obtenerProductos();
      this.getCustomers();

    }
  }
  toggleHeaderOrder() {
    this.showHeaderOrder = !this.showHeaderOrder;
  }
  checkIfLoggedIn(): boolean {
    const token = localStorage.getItem('token');
    return !!token;
  }
  getOrders(type:any): void {
    this.orders = [];
    if(type == 'date')
      this.orderService.getOrders(this.datePipe.transform(this.searchStartDate, 'yyyy-MM-dd'), this.datePipe.transform(this.searchEndDate, 'yyyy-MM-dd'))
        .subscribe(orders => {
          this.orders = orders;
          this.filteredOrders = orders;
          this.filterOrders();
        });
    else
      this.orderService.getOrdersByStatus(this.searchStatus)
      .subscribe(orders => {
        this.orders = orders;
        this.filteredOrders = orders;
        this.filterOrders();
      });
  }
  filterOrders(): void {
    if (this.searchText.trim() !== '') {
      this.filteredOrders = this.orders?.filter(order => {
        return ['order_number', 'customer_email', 'customer_phone', 'customer_documentNumber', 'customer_name', 'delivery_date', 'status']
          .some(key => order[key]?.toLowerCase().includes(this.searchText.toLowerCase()));
      });
    } else {
      this.filteredOrders = this.orders;
    }
  }
  openEditModal(order: any, type: any): void {
    this.order = order;
    this.actionType = type;
    if (Object.keys(order).length === 0) {
      this.order.order_number = this.order_numer_sug;
    }
  }
  updated_order(): void {
    const currentDate: Date = new Date();
    // Obtener los componentes de la fecha y hora
    const year: number = currentDate.getFullYear();
    const month: number = currentDate.getMonth() + 1; // Los meses comienzan desde 0
    const day: number = currentDate.getDate();
    const hours: number = currentDate.getHours();
    const minutes: number = currentDate.getMinutes();
    const seconds: number = currentDate.getSeconds();

    // Formatear la fecha y hora
    const formattedDate: string = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    this.order.total = parseFloat(this.order.products.reduce((total: number, product: any) => {
      return total + (product.quantity * product.price_sale);
    }, 0));
    this.order.updated_at = formattedDate;
    this.orderService.updateOrder(this.order.id, this.order).subscribe((data: any) => {
      // Lógica después de actualizar la orden, si es necesario
    });

    this.getOrders('date');
  }
  created_order(): void {
    const currentDate: Date = new Date();
    // Obtener los componentes de la fecha y hora
    const year: number = currentDate.getFullYear();
    const month: number = currentDate.getMonth() + 1; // Los meses comienzan desde 0
    const day: number = currentDate.getDate();
    const hours: number = currentDate.getHours();
    const minutes: number = currentDate.getMinutes();
    const seconds: number = currentDate.getSeconds();

    // Formatear la fecha y hora
    const formattedDate: string = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

    this.order.created_at = formattedDate;
    this.order.updated_at = formattedDate;
    this.order.total = parseFloat(this.order.products.reduce((total: number, product: any) => {
      return total + (product.quantity * product.price_sale);
    }, 0));
    this.orderService.createOrder(this.order).subscribe((data: any) => {
      // Lógica después de crear una nueva orden, si es necesario
    });
    this.getOrders('date');
  }
  saveOrder() {
    if (this.actionType === 'update') {
      this.updated_order();
      this.getOrders('date')
    } else if (this.actionType === 'new') {
      this.created_order();
      this.getOrders('date')
    }
  }

  removeProduct(product: any): void {
    const index = this.order.products.indexOf(product);
    if (index !== -1) {
      this.order.products.splice(index, 1);
    }
  }
  addProduct(): void {
    if (!this.order.products) {
      this.order.products = [];
    }
    this.order.products.push({
      sku: '',
      name: '',
      price_sale: 0,
      quantity: 1,
      iva: false,
      iva_value: 0,
      unit : '',
      category: '',
    });
  }
  obtenerProductos(): void {
    this.productService.getProducts()
      .subscribe(
        (data: any) => {
          this.products = data;
        },
      );
  }
  openPdfModal(order: any,type:any): void {
    if (type == 'unique')
      this.pdfData = this.sanitizer.bypassSecurityTrustResourceUrl('https://app.buyfrescapp.com:5000/api/order/generate_pdf/' + order);
    else
      this.pdfData = this.sanitizer.bypassSecurityTrustResourceUrl('https://app.buyfrescapp.com:5000/api/reports/picking/' + this.searchStartDate + '/' + this.searchEndDate);
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
  filteredCustomers() {
    if (!this.searchText) {
      return this.customers;
    }
    return this.customers.filter(customer =>
      customer.name.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }
  onCustomerSelect() {
    const selectedCustomer = this.customers.find(customer => customer.id === this.selectedCustomerId);
    if (selectedCustomer) {
      this.order.customer_name = selectedCustomer.name;
      this.order.customer_email = selectedCustomer.email;
      this.order.customer_phone = selectedCustomer.phone;
      this.order.customer_documentNumber = selectedCustomer.document;
      this.order.customer_documentType = selectedCustomer.document_type;
      this.order.deliveryAddress = selectedCustomer.address;
    }
  }
  onProductSelect(product: { id: any; name: any; sku: any; price_sale: any; iva: any; iva_value: any; unit: any; category:any; }): void {
    const selectedProduct = this.products.find(p => p.id === product.id);
    if (selectedProduct) {
      product.name = selectedProduct.name;
      product.sku = selectedProduct.sku;
      product.price_sale = selectedProduct.price_sale;
      product.iva = selectedProduct.iva;
      product.iva_value = selectedProduct.iva_value;
      product.unit = selectedProduct.unit;
      product.category = selectedProduct.category;
    }
  }
  sync_allegra(order_number: any) {
    this.alegraService.send_invoice(order_number).subscribe(
      (res: any) => {
          if (res.status == '201'){
          this.statusCodeAlegra = '201';
          this.messageAlegra = res.message || 'Factura creada exitosamente.'; // Ajusta este mensaje según lo que devuelva la API
        }else{
          this.statusCodeAlegra == '400';
          this.messageAlegra = res.error?.message || 'Ocurrió un error'; // Ajusta el mensaje de error según sea necesario
        }
        this.getOrders('date')
      },
      (error) => {
        this.statusCodeAlegra = error.status.toString(); // Obtiene el código de estado del error
        this.messageAlegra = error.error?.message || 'Ocurrió un error'; // Ajusta el mensaje de error según sea necesario
        this.getOrders('date')
      }
    );
  }
  get_invoice(order_number: any){
    this.alegraService.get_invoice(order_number).subscribe(
      (res: any) => {
        this.facturaData = this.sanitizer.bypassSecurityTrustResourceUrl(res);

      }
    );
  }
  delete_order(id: any){
    this.orderService.deleteOrder(id).subscribe(
      (res: any) => {
        this.getOrders('date')
      }
    );
  }
  sort(column: string) {
    if (!this.filteredOrders || this.filteredOrders.length === 0) {
      return; // No hacer nada si filteredOrders es indefinido o está vacío
    }

    if (this.sortColumn === column) {
      // Si ya está ordenado por esta columna, invertir la dirección
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // Si se selecciona una nueva columna, ordenar por ella en orden ascendente
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }

    // Ordenar filteredOrders según la columna y dirección
    this.filteredOrders.sort((a, b) => {
      const valueA = a[this.sortColumn];
      const valueB = b[this.sortColumn];

      if (valueA == null) return this.sortDirection === 'asc' ? 1 : -1;
      if (valueB == null) return this.sortDirection === 'asc' ? -1 : 1;

      if (valueA < valueB) return this.sortDirection === 'asc' ? -1 : 1;
      if (valueA > valueB) return this.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }
  sendSyncOrder(orderNumber:any) {
    this.wooService.get_order(orderNumber).subscribe((response:any) => {
      if (response) {
        this.successMessage = response.message || 'Orden sincronizada correctamente!';
        this.getOrders('date')
      } else {
        this.failedMessage = response.message || 'Falló la sincronizacón de la orden!';
        this.getOrders('date')
      }
    });
  }
  getEvidence(orderNumber:any){
    this.routeService.getStopNumber(orderNumber).subscribe(
      (res: any) => {
        this.titleEvidence = res.payment_method;
        if(res.evidence == undefined){
          this.evidence == 'Sin evidencia'
          this.titleEvidence = 'Sin evidencia'
        }else{
            this.evidence = this.sanitizer.bypassSecurityTrustResourceUrl("https://app.buyfrescapp.com:5000/api/route/route/evidence/"+res.evidence);
            const fileExtension = res.evidence.split('.').pop().toLowerCase();
            let mimeType: string;
            switch (fileExtension) {
              case 'pdf':
                mimeType = 'application/pdf';
                break;
              case 'jpg':
              case 'jpeg':
                mimeType = 'image/jpeg';
                break;
              case 'png':
                mimeType = 'image/png';
                break;
              case 'gif':
                mimeType = 'image/gif';
                break;
              case 'txt':
                mimeType = 'text/plain';
                break;
              case 'html':
                mimeType = 'text/html';
                break;
              // Agrega más casos según sea necesario
              default:
                mimeType = 'application/octet-stream'; // Tipo MIME por defecto para archivos desconocidos
                break;
            }

            // Asignar el tipo de evidencia y la URL segura
            this.typeEvidence = mimeType;
          }
      }
    );
  }
  camposCompletos(): boolean {
    if (
        !this.order?.delivery_date ||
        !this.order?.deliverySlot ||
        !this.order?.paymentMethod ||
        !this.order?.deliveryAddress ||
        !this.order?.status ||
        !this.order?.seller_name ||
        !this.order?.source ||
        !this.order?.driver_name) {
      return false;
    }
    return true;
  }
  navigateToOrden(orderNumber: string) {
    this.router.navigate(['/orden', orderNumber]);
  }
}

