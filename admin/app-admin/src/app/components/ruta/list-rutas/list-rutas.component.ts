import { Component } from '@angular/core';
import { RoutesService } from '../../../services/routes.service';
import { Router } from '@angular/router';
import { toInteger } from '@ng-bootstrap/ng-bootstrap/util/util';

@Component({
  selector: 'app-list-rutas',
  templateUrl: './list-rutas.component.html',
  styleUrl: './list-rutas.component.css'
})
export class ListRutasComponent {
  public filteredRoutes:any = [];
  public routes:any = [];
  public searchText = '';
  public messageRoute = '';
  public newRouteDate: string = '';
  public newRouteDriver: string = '';
  public newCost : number = 0;
  public drivers: string[] = ['Carlos','Diago', 'Jhony','Sebas','Cata']
  public selectedRoute:any = '';
  routeConsolidada: any = null;
  constructor(
    private routesService: RoutesService,
    private router: Router,

  ) { }

  ngOnInit(): void {
    this.getRoutes();
    //this.filterRoutes();
  }
  hasRole(requiredRoles: string[]): boolean {
    return requiredRoles.some(r => localStorage.getItem('role')?.includes(r));
  }
  getRoutes(){
    this.routesService.getRoutes().subscribe(
      (res: any) => {
        this.routes = res;
        this.filteredRoutes = this.routes;
      }
      )
  }
  filterRoutes() {
    //this.filteredRoutes = this.routes.filter(route => route.date.includes(this.searchText));
  }

  createRoute() {
    this.routesService.createRoute(this.newRouteDate,this.newRouteDriver,this.newCost).subscribe(
      (res: any) => {
        this.messageRoute = 'Nueva ruta creada exitosamente!';
        this.getRoutes();
        this.filteredRoutes = this.routes;
      }
    )
  }
  deleteRoute(route : any) {
    this.routesService.delteRoute(route.id).subscribe(
      (res: any) => {
        this.messageRoute = 'Ruta eliminada exitosamente!';
        this.getRoutes();
        this.filteredRoutes = this.routes;
      }
    )
  }

  navigateToRoute(routNumber: number) {
    this.router.navigate(['/stops', routNumber]);
  }
  programarRuta(route:any){

  }
  calculateTotalToCharge(routeId: string) {
    const route = this.filteredRoutes.find((route: any) => route.id === routeId);
    if (route) {
      let total = 0;
      route.stops.forEach((stop: any) => {
        total += stop.total_to_charge; // Sumar el total a cobrar de cada parada
      });
      return total;
    }
    return 0
  }
  calculateTotalPayment(routeId: string,tipo:String){
    const route = this.filteredRoutes.find((route: any) => route.id === routeId);
    if (route) {
      let total = 0;
      route.stops.forEach((stop: any) => {
        if(stop.payment_method == tipo){
          total += Number(stop.total_charged);
        }
      });
      return total;
    }
    return 0
  }

  calculateTotalStops(routeId: string) {
    const route = this.filteredRoutes.find((route: any) => route.id === routeId);
    if (route) {
      return route.stops.length;
    }
    return 0
  }
  openEditRoute(route: any): void {
    // Clona el objeto de la ruta seleccionada
    this.selectedRoute = { ...route };

    // Ordena las paradas basándose en el atributo 'order'
    this.selectedRoute.stops = this.selectedRoute.stops.sort((a: any, b: any) => a.order - b.order);
}

// Función para mover una parada hacia arriba
moveStopUp(index: number): void {
    if (index > 0) {
        const stops = this.selectedRoute.stops;
        [stops[index - 1], stops[index]] = [stops[index], stops[index - 1]];
    }
}

// Función para mover una parada hacia abajo
moveStopDown(index: number): void {
    const stops = this.selectedRoute.stops;
    if (index < stops.length - 1) {
        [stops[index], stops[index + 1]] = [stops[index + 1], stops[index]];
    }
}

// Guardar cambios en la ruta
updateRoute(): void {
    // Actualiza los datos de la ruta en el servicio o base de datos aquí
    this.routesService.updateRoute(this.selectedRoute).subscribe((data: any) => {
        // Acciones después de guardar los cambios
        this.getRoutes(); // Actualiza la lista de rutas en la interfaz
    });
}
getRouteConsolidated(route_number:any){
  this.routesService.getRouteConsolidated(route_number).subscribe(
    (res: any) => {
      this.routeConsolidada = res;
    }
  )}
}
