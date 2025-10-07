import { Component } from '@angular/core';
import { OrderService } from '../../services/order.service';

@Component({
  selector: 'app-pedidos-report',
  templateUrl: './pedidos-report.component.html',
  styleUrl: './pedidos-report.component.css'
})
export class PedidosReportComponent {
  constructor(    private orderService: OrderService) { }
fechaHoy: string = new Date().toISOString().substring(0, 10);
fechaSeleccionada: string = this.fechaHoy;

  descargarPDF() {
      window.open(
        'https://app.buyfrescapp.com:5000/api/reports/picking/' + this.fechaSeleccionada + '/' + this.fechaSeleccionada,
        '_blank');
  }
}
