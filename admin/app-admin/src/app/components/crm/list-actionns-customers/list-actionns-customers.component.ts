import { Component } from '@angular/core';
import { ActionService } from '../../../services/action.service';
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-list-actionns-customers',
  templateUrl: './list-actionns-customers.component.html',
  styleUrl: './list-actionns-customers.component.css'
})
export class ListActionnsCustomersComponent {
  actions:  any[] | undefined;
  filteredActions: any[] | undefined;
  searchText: string = '';
  messageAction: string ='';
  statusCodeAction : string = '' ;
  actionSelect :any;
  managers: string[] = ['Ferney', 'Cata', 'Diago','Saco'];
  today = new Date();
  yyyy = this.today.getFullYear();
  mm = String(this.today.getMonth() + 1).padStart(2, '0'); // Los meses van de 0 a 11, por eso sumamos 1
  dd = String(this.today.getDate()).padStart(2, '0');
  searchDate = `${this.yyyy}-${this.mm}-${this.dd}`;
  selectedManager: string | null = null;
  constructor(
    private actionService: ActionService,
    private router: Router,
    private datePipe: DatePipe
  ){}
  ngOnInit(): void {
    this.getActions();
    this.selectedManager = localStorage.getItem('username');
  }
  navigateToaAction(actionNumber: number) {
      this.router.navigate(['/edit_action', actionNumber]);
  }
  filterActions() {
    if (this.searchText.trim() !== '') {
      this.filteredActions = this.actions?.filter(action => {
        const searchTextLower = this.searchText.toLowerCase();
        return (
          (action.customer.name && action.customer.name.toLowerCase().includes(searchTextLower)) ||
          (action.customer.address && action.customer.address.toLowerCase().includes(searchTextLower)) ||
          (action.customer.phone && action.customer.phone.toLowerCase().includes(searchTextLower)) ||
          (action.customer.email && action.customer.email.toLowerCase().includes(searchTextLower)) ||
          (action.manager && action.manager.toLowerCase().includes(searchTextLower)) ||
          (action.status && action.status.toLowerCase().includes(searchTextLower)) ||
          (action.actionComment && action.actionComment.toLowerCase().includes(searchTextLower)) ||
          (action.solutionType && action.solutionType.toLowerCase().includes(searchTextLower)) ||
          (action.solutionComment && action.solutionComment.toLowerCase().includes(searchTextLower))
        );
      });
    } else {
      this.filteredActions = this.actions;
    }
  }


  newAction() {
    this.router.navigate(['/newAction']);
  }
  getActions(){
    this.actionService.getActions(this.searchDate).subscribe(
      (res: any) => {
        this.actions = res;
        this.filteredActions = this.actions;
      }
      )
  }

  delete_action(actionNumnber:any){
    this.actionService.deleteAction(actionNumnber).subscribe(
      (res: any) => {
        this.getActions();
        this.messageAction = 'Accion eliminada exitosamente!';
        this.statusCodeAction = res.statusCode || '200';
        setTimeout(() => {
          this.messageAction = '';
        }, 3000);
      },
      (error: any) => {
        this.messageAction = 'Fallo al eliminar la accion.';
        this.statusCodeAction = error.status || '500';
        setTimeout(() => {
          this.messageAction = '';
        }, 3000);
      }
    );
  }
  resolver(actionNumnber:any){
    this.router.navigate(['/edit_action',actionNumnber]);
  }
  viewAction(action:any){
    this.actionSelect = action;
  }
}

