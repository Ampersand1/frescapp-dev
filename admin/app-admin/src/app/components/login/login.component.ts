import { Component } from '@angular/core';
import { AuthenticationService } from '../../services/authentication.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username: string = '';
  password: string = '';
  error: string = '';
  flag: boolean = false;

  constructor(private authService: AuthenticationService, private router: Router) {}

  login(): void {
    // -----------------------------------------------------------
    // CÓDIGO ORIGINAL (COMENTADO PARA EVITAR CONEXIÓN AL BACKEND)
    // -----------------------------------------------------------
    /*
    if (this.username === '' || this.password === '') {
      this.flag = true;
      this.error = 'Por favor, ingrese nombre de usuario y contraseña.';
      return;
    }

    this.authService.login(this.username, this.password).subscribe(
      (response: any) => {
        localStorage.setItem('username', this.username);
        localStorage.setItem('token', response?.token || '');

        const roles = response?.user_data?.role;
        if (Array.isArray(roles)) {
          localStorage.setItem('role', JSON.stringify(roles));
        } else {
          localStorage.setItem('role', JSON.stringify([])); // fallback seguro
        }

        this.router.navigate(['/home']);
      },
      (error: any) => {
        this.flag = true;
        this.error = 'Nombre de usuario o contraseña incorrectos.';
      }
    );
    */

    // -----------------------------------------------------------
    // CÓDIGO NUEVO (FORZAR ENTRADA / BYPASS)
    // -----------------------------------------------------------
    console.log("🔓 MODO DIOS ACTIVADO: Entrando a la fuerza...");

    // 1. Guardamos un token falso (para engañar al guardián de rutas)
    localStorage.setItem('token', 'TOKEN_FALSO_12345_ADMIN');

    // 2. Guardamos un nombre de usuario cualquiera
    localStorage.setItem('username', 'SuperAdmin');

    // 3. Guardamos el ROL DE ADMINISTRADOR (Vital para que aparezca el menú)
    // Importante: Tiene que ser una lista ['administrador'] convertida a texto
    localStorage.setItem('role', JSON.stringify(['administrador']));

    // 4. Redirigimos a la página principal
    this.router.navigate(['/home']);
  }
}