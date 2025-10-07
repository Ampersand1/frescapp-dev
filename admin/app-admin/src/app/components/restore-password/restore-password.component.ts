import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthenticationService } from '../../services/authentication.service';

@Component({
  selector: 'app-restore-password',
  templateUrl: './restore-password.component.html',
  styleUrls: ['./restore-password.component.css']
})
export class RestorePasswordComponent implements OnInit {
  password1: string = '';
  password2: string = '';
  mensajeError: string = '';
  mensajeSuccess: string = '';
  user_id: string = '';

  constructor(
    private route: ActivatedRoute,
    private authService: AuthenticationService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.user_id = params['user_id'];
    });
  }

  restablecer() {
    if (this.password1 !== this.password2) {
      this.mensajeError = 'Las contraseñas no coinciden.';
      return;
    }

    if (!this.user_id) {
      this.mensajeError = 'No se encontró el user_id. Por favor intenta nuevamente.';
      return;
    }

    this.authService.changePassword(this.user_id, this.password1)
      .subscribe(
        () => {
          this.mensajeSuccess = 'Se realizó el cambio de contraseña correctamente, vuelve a intentar ingresar en la app. Gracias.';
        },
        (error: any) => {
          this.mensajeError = 'No se realizó el cambio de contraseña, por favor intentalo más tarde o comunícate a nuestro Whatsapp 3115455042';
        }
      );
  }
}
