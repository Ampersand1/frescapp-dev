import { Component,  OnInit } from '@angular/core';
import { OrderService } from '../../services/order.service';
import { AlegraService } from '../../services/alegra.service';
import { DomSanitizer } from '@angular/platform-browser';
import { RoutesService } from '../../services/routes.service';

@Component({
  selector: 'app-cartera',
  templateUrl: './cartera.component.html',
  styleUrl: './cartera.component.css'
})
export class CarteraComponent implements OnInit {
  constructor(
    private orderService: OrderService
    ,private alegraService: AlegraService
    ,private sanitizer: DomSanitizer
    ,private routeService : RoutesService


  ) { }
  orders:any = [];
  total_cartera = 0;
  total_orders = 0;
  searchText:String ='';
  ordersFiltered: any = [];
  evidence: any = null;
  titleEvidence: string = '';
  facturaData: any = null;
  pdfData: any = null;
  typeEvidence: string = '';
  stopSelect = {
    order : 0,
    order_number: 0,
    client_name: '',
    address: '',
    slot: '',
    total_to_charge: 0,
    total_charged: 0,
    payment_date: null,
    status: '',
    evidence: '',
    open_hour: '',
    payment_method: '',
  };
  public methedoPayments = ["Davivienda", "Bancolombia",  "Efectivo"];
  public statusStops = ["Por entregar", "Pendiente de pago", "Pagada"];
  public selectedFile: File | null = null;
  public routeNumber: number = 0;
  public routeSelect: any;
  ngOnInit(): void {
    this.getOrders();
  }
  getOrders(){
    this.orderService.getOrdersByStatus("Pendiente de pago")
    .subscribe(orders => {
      this.orders = orders;
      this.ordersFiltered = orders; // Inicializa ordersFiltered con todos los pedidos
      this.total_cartera = this.ordersFiltered.reduce((sum: number, order: any) => {
        // Asegúrate de que order.total es un número y no es null/undefined
        const orderTotal = order.total - order.totalPayment  ? Number(order.total - order.totalPayment ) : 0;
        return sum + orderTotal;
      }, 0);
      this.total_cartera = parseFloat(this.total_cartera.toFixed(2));
      this.total_orders = this.orders.length;
    });
  }
  filterorders() {
    const searchTextLower = this.searchText.trim().toLowerCase();

    if (searchTextLower !== '') {
      this.ordersFiltered = this.orders.filter((order: any) => {
        const fieldsToSearch = [
          order.cliente,
          order.delivery_date,
          order.customer_name,
          order.order_number,
          order.customer_email,
          order.customer_phone,
          order.deliveryAddress,
          order.status,
          order.paymentMethod,
          order.driver_name
        ];

        return fieldsToSearch.some(field =>
          (field ?? '').toString().toLowerCase().includes(searchTextLower)
        );
      });
    } else {
      this.ordersFiltered = this.orders;
    }

    this.total_cartera = this.ordersFiltered.reduce((sum: number, order: any) => {
      const total = Number(order.total ?? 0);
      const payment = Number(order.totalPayment ?? 0);
      return sum + (total - payment);
    }, 0);

    this.total_cartera = parseFloat(this.total_cartera.toFixed(2));
    this.total_orders = this.ordersFiltered.length;
  }

  daysMora(order: any): number {
    if (!order.delivery_date) {
      return 0;
    }
    const deliveryDate = new Date(order.delivery_date);
    const today = new Date();
    // Calcula la diferencia en milisegundos
    const diffMs = today.getTime() - deliveryDate.getTime();
    // Convierte la diferencia a días
    return Math.floor(diffMs / (1000 * 3600 * 24));
  }
  get_invoice(order_number: any){
    this.alegraService.get_invoice(order_number).subscribe(
      (res: any) => {
        this.facturaData = this.sanitizer.bypassSecurityTrustResourceUrl(res);

      }
    );
  }
  openPdfModal(order: any): void {
      this.pdfData = this.sanitizer.bypassSecurityTrustResourceUrl('https://app.buyfrescapp.com:5000/api/order/generate_pdf/' + order);
  }
  onStatusChange(event: any) {
    const selectedStatus = event;
    if (selectedStatus === "Pagada") {
      this.stopSelect.total_charged = this.stopSelect.total_to_charge;
    }else {
      this.stopSelect.total_charged = 0;
      this.stopSelect.payment_date = null;
    }
  }
  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      // Generar un nombre de archivo basado en el número de ruta y orden de parada
      const fileExtension = file.name.split('.').pop();
      const fileName = `${this.routeNumber}_${this.stopSelect.order_number}.${fileExtension}`;

      // Crear un archivo con el nuevo nombre
      const renamedFile = new File([file], fileName, { type: file.type });

      this.selectedFile = renamedFile; // Guardar el archivo renombrado
      this.stopSelect.evidence = fileName; // Guardar solo el nombre en el campo 'evidence' del stopSelect
    }
  }

  saveStop() {
  const stops = this.routeSelect.stops
  const stopIndex = stops.findIndex(
    (stop: { order_number: any }) =>
      stop.order_number === this.stopSelect.order_number
  );
    if (stopIndex !== -1) {
      // Actualizar el stop con los nuevos datos
      this.routeSelect.stops[stopIndex] = { ...this.routeSelect.stops[stopIndex], ...this.stopSelect };

      const formData = new FormData();

      // Añade la ruta como JSON
      formData.append('route', JSON.stringify(this.routeSelect));

      // Añade el archivo, si está seleccionado
      if (this.selectedFile) {
        formData.append('file', this.selectedFile, this.selectedFile.name);
      }
      this.routeService.updateStop(this.routeSelect, this.selectedFile).subscribe(
        (response: any) => {
          this.getOrders(); // Actualizar la lista de pedidos después de guardar
          this.filterorders(); // Aplicar el filtro después de actualizar
        },
        (error: any) => {
          console.error('Error al guardar la parada', error);
        }
      );
    } else {
      console.error('Parada no encontrada');
    }
  }

  navigateToStop(order: any) {
    this.routeService.getRouteByDate(order.delivery_date).subscribe(
      (res: any) => {
        this.routeSelect = JSON.parse(res);

      }
    );
    this.routeService.getStopNumber(order.order_number).subscribe(
      (res: any) => {
        this.routeService.getStopNumber(order.order_number).subscribe(
          (res: any) => {
            this.stopSelect = res
          }
        );
      }
    );
  }

}

