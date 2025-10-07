import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthenticationService } from '../../services/authentication.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  isLoggedIn: boolean = false;
  role:string | null ='';

  constructor(private authService: AuthenticationService, private router: Router) { }

  ngOnInit(): void {
    this.checkToken();
    this.role = localStorage.getItem('role');
  }

  checkToken() {
    const token = localStorage.getItem('token');
    if (token) {
      this.authService.checkToken(token).subscribe(
        () => {
          this.isLoggedIn = true;
        },
        error => {
          console.error('Error al verificar el token:', error);
          this.isLoggedIn = false;
          this.router.navigate(['/login']); // Redirigir a la página de inicio de sesión si el token no es válido
        }
      );
    } else {
      this.isLoggedIn = false;
      this.router.navigate(['/login']); // Redirigir a la página de inicio de sesión si no hay token almacenado
    }
  }

  redirectToLogin() {
    this.router.navigate(['/login']);
  }
}
