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
  }
}
