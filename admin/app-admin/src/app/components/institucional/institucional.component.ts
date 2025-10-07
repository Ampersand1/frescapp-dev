import { Component } from '@angular/core';


export interface Cliente {
  nombre: string;
  direccion: string;
  telefono: string;
  nit: string;
  email: string;
}
@Component({
  selector: 'app-institucional',
  templateUrl: './institucional.component.html',
  styleUrl: './institucional.component.css'
})
export class InstitucionalComponent {


seccionActiva: string = 'pedido';
colapsado: boolean = false;

  clientes: Cliente[] = [];
clienteSeleccionado: Cliente | null = null;
seleccionarCliente(cliente: Cliente): void {
  this.clienteSeleccionado = cliente;
  this.seccionActiva = 'pedido'; // Por si está en otra sección
}
}
