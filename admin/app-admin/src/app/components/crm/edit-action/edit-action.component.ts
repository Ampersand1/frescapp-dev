import { Component, OnInit } from '@angular/core';
import { ActionService } from '../../../services/action.service';
import { Router, ActivatedRoute } from '@angular/router';
import * as mapboxgl from 'mapbox-gl';
import  { Modal } from 'bootstrap';

@Component({
  selector: 'app-edit-action',
  templateUrl: './edit-action.component.html',
  styleUrls: ['./edit-action.component.css']
})
export class EditActionComponent implements OnInit {
  actionObject: any = {
    dateAction: '',
    dateSolution: '',
    type: '',
    customer: {},
    orderNumber: '',
    manager: '',
    status: '',
    actionComment: '',
    solutionType: '',
    solutionComment: '',
    latitude: null,
    longitude: null
  };

  searchTerm: string = ''; // Término de búsqueda
  customers: any[] = []; // Lista completa de clientes
  filteredCustomers: any[] = []; // Clientes filtrados para la búsqueda
  solutions: string[] = [];
  public map: any;
  modal?: Modal;
  constructor(
    private actionService: ActionService,
    private router: Router,
    private route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.loadAction();
    this.getCurrentLocation();
    this.loadCustomers();
    const modalElement = document.getElementById('customerModal');
    if (modalElement) {
      this.modal = new Modal(modalElement);
    } else {
      console.error('Modal element not found');
    }
  }

  loadAction() {
    const actionId = this.route.snapshot.paramMap.get('action');
    if (actionId) {
      this.actionService.getAction(actionId).subscribe(
        (data: { type: { solutions: string[]; }; }) => {
          this.actionObject = data;
          this.solutions = data.type.solutions;
          this.initializeMap();
        },
        (error: any) => {
          console.error('Error al cargar la acción:', error);
        }
      );
    }
  }

  // Cargar la lista de clientes desde el servicio
  loadCustomers() {
    this.actionService.getPotentialCustomers().subscribe(
      (data:any) => {
        this.customers = data;
        this.filteredCustomers = this.customers;
      },
      (error:any) => {
        console.error('Error al cargar los clientes:', error);
      }
    );
  }

  // Buscar cliente en la lista
  searchCustomer() {
    if (this.searchTerm) {
      this.filteredCustomers = this.customers.filter(customer =>
        customer.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        customer.email.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        customer.phone.toString().includes(this.searchTerm) ||
        customer.address.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    } else {
      this.filteredCustomers = this.customers;
    }
  }

  // Seleccionar cliente y asignarlo a la acción
  selectCustomer(customer: any) {
    this.actionObject.customer = customer;
    this.initializeMap();
    if (this.modal) {
      this.modal.hide();
    }
  }

  // Inicializa el mapa
  initializeMap() {
    if (this.actionObject.customer.latitude && this.actionObject.customer.longitude) {
      this.map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v12',
        projection: { name: 'mercator' },
        zoom: 15,
        center: [
          parseFloat(this.actionObject.customer.longitude),
          parseFloat(this.actionObject.customer.latitude)
        ],
        accessToken: 'pk.eyJ1Ijoidm1kaWFnb3YiLCJhIjoiY2x4MGtxY2NlMDFxdDJycTdrdXhvYWE4byJ9.rQb2uBaS48sEyvpbdMj14Q'
      });

      new mapboxgl.Marker()
        .setLngLat([
          parseFloat(this.actionObject.customer.longitude),
          parseFloat(this.actionObject.customer.latitude)
        ])
        .addTo(this.map);
    }
  }

  getCurrentLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.actionObject.latitude = position.coords.latitude;
          this.actionObject.longitude = position.coords.longitude;
        },
        (error) => {
          console.error('Error obteniendo la ubicación:', error);
        }
      );
    } else {
      console.error('Geolocalización no es soportada por el navegador');
    }
  }

  completar() {
    const bogotaTime = new Date().toLocaleString("en-US", { timeZone: "America/Bogota" });
    this.actionObject.dateSolution = new Date(bogotaTime).toISOString();
    this.getCurrentLocation();

    this.actionService.editAction(this.actionObject.actionNumber, this.actionObject).subscribe((res: any) => {
      this.router.navigate(['/crm']);
    });
  }

  backList() {
    this.router.navigate(['/crm']);
  }
  openCustomers(){
    if (this.modal) {
      this.modal.show();
    }
  }
}
