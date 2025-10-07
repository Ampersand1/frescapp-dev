import { Component } from '@angular/core';
import { RoutesService } from '../../../services/routes.service';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-stops',
  templateUrl: './stops.component.html',
  styleUrl: './stops.component.css'
})
export class StopsComponent {
  public stops: any = [];
  public routeNumber: number = 0;
  public routeSelect: any;
  public stopSelect: any;
  public methedoPayments = ["Davivienda", "Bancolombia",  "Efectivo"];
  public statusStops = ["Por entregar", "Pendiente de pago", "Pagada"];
  public selectedFile: File | null = null; // Almacena el archivo seleccionado

  constructor(
    private routesService: RoutesService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.route.params.subscribe(params => {
      this.routeNumber = params['route_number'];
    });
  }

  ngOnInit(): void {
    this.getStops();
  }

  getStops() {
    this.routesService.getRoute(this.routeNumber).subscribe(
      (res: any) => {
        this.routeSelect = res;
        this.stops = res["stops"].sort((a: any, b: any) => a.order - b.order);
        this.stopSelect = this.stops[0];
      }
    );
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

  navigateToStop(stop: any) {
    this.stopSelect = stop;
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      // Generar un nombre de archivo basado en el número de ruta y orden de parada
      const fileExtension = file.name.split('.').pop();
      const fileName = `${this.routeNumber}_${this.stopSelect.order}.${fileExtension}`;

      // Crear un archivo con el nuevo nombre
      const renamedFile = new File([file], fileName, { type: file.type });

      this.selectedFile = renamedFile; // Guardar el archivo renombrado
      this.stopSelect.evidence = fileName; // Guardar solo el nombre en el campo 'evidence' del stopSelect
    }
  }

  saveStop() {
    const formData = new FormData();

    // Añade la ruta como JSON
    formData.append('route', JSON.stringify(this.routeSelect));

    // Añade el archivo, si está seleccionado
    if (this.selectedFile) {
      formData.append('file', this.selectedFile, this.selectedFile.name);
    }
    this.routesService.updateStop(this.routeSelect, this.selectedFile).subscribe(
      (response: any) => {
        console.log('Parada guardada y ruta actualizada', response);
      },
      (error: any) => {
        console.error('Error al guardar la parada', error);
      }
    );
  }


  navigateToRoute() {
    this.router.navigate(['/rutas']);
  }
}
