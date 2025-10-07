import { Component } from '@angular/core';
import { CostsService } from '../../services/costs.service';

@Component({
  selector: 'app-costs',
  templateUrl: './costs.component.html',
  styleUrl: './costs.component.css'
})
export class CostsComponent {
  costs: any[] = [];
  currentCost: any = {};
  editingCost: boolean = false;
  months: string[] = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];
  messageCost = '';
  statusCodeCost = '';
  constructor(
    private costService: CostsService
  ){}
  ngOnInit(): void {
    this.getCosts()
  }
  openNewCostModal() {
    this.currentCost = { typeCost: '', detail: '', amount: 0, typePeriod: '', period: '' };
    this.editingCost = false;
  }
  getCosts(){
    this.costService.getCostos().subscribe(
      (res: any) => {
        this.costs = res;
      }
      )
  }
  editCost(cost: any) {
    this.currentCost = { ...cost };
    this.editingCost = true;
  }

  saveCost() {
    if (this.editingCost) {
      this.costService.updateCosto(this.currentCost).subscribe(
        (res: any) => {
          this.getCosts();
          this.messageCost = 'Costo actualizado exitosamente!';
          this.statusCodeCost = res.statusCode || '200';
          setTimeout(() => {
            this.messageCost = '';
          }, 3000);
        },
        (error: any) => {
          this.messageCost = 'Fallo al actualizar el costo.';
          this.statusCodeCost = error.status || '500';
          setTimeout(() => {
            this.messageCost = '';
          }, 3000);
        }
      );
    } else {
      this.costService.createCosto(this.currentCost).subscribe(
        (res: any) => {
          this.getCosts();
          this.messageCost = 'Costo creado exitosamente!';
          this.statusCodeCost = res.statusCode || '200';
          setTimeout(() => {
            this.messageCost = '';
          }, 3000);
        },
        (error: any) => {
          this.messageCost = 'Fallo al crear el costo.';
          this.statusCodeCost = error.status || '500';
          setTimeout(() => {
            this.messageCost = '';
          }, 3000);
        }
      );
    }
  }

  deleteCost(cost: any) {
    this.costService.deleteCosto(cost.id).subscribe(
      (res: any) => {
        this.getCosts();
        this.messageCost = 'Costo eliminado exitosamente!';
        this.statusCodeCost = res.statusCode || '200';
        setTimeout(() => {
          this.messageCost = '';
        }, 3000);
      },
      (error: any) => {
        this.messageCost = 'Fallo al eliminar el costo.';
        this.statusCodeCost = error.status || '500';
        setTimeout(() => {
          this.messageCost = '';
        }, 3000);
      }
    );
  }

  resetPeriodDetail() {
    this.currentCost.periodDetail = '';
  }
}
