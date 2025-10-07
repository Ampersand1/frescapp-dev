import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthenticationService } from '../../services/authentication.service';

@Component({
  selector: 'app-delete-account',
  templateUrl: './delete-account.component.html',
  styleUrls: ['./delete-account.component.css']
})
export class DeleteAccountComponent {
  password: string = '';
  mensajeError: string = '';
  mensajeSuccess: string = '';
  user_email: string = '';

  constructor(
    private route: ActivatedRoute,
    private authService: AuthenticationService
  ) {
    this.route.queryParams.subscribe(params => {
      this.user_email = params['user_id'];
    });
  }

  delete() {
    this.authService.deleteAccount(this.user_email, this.password)
    .subscribe(
      () => {
        this.mensajeSuccess = 'Se eliminó la cuenta '+ this.user_email+' correctamente';
      },
      (error: any) => {
        this.mensajeError = 'No se eliminó correctamente la cuenta, por favor comunicate con nuestro Whatsapp 3115455042';
      }
    );
  }
}
