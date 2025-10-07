import { Component, OnInit } from '@angular/core';
import { AuthenticationService } from '../../services/authentication.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.css']
})
export class NavigationBarComponent implements OnInit {

  role: string[] = [];
  isMenuCollapsed = true;

  constructor(
    private authService: AuthenticationService,
    private router: Router
  ) { }

  ngOnInit(): void {
    const roleString = localStorage.getItem('role');
    this.role = roleString ? JSON.parse(roleString) : [];
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }

  hasRole(requiredRoles: string[]): boolean {
    return requiredRoles.some(r => this.role.includes(r));
  }

  toggleMenu(): void {
    this.isMenuCollapsed = !this.isMenuCollapsed;
  }

  logout(): void {
    const token = localStorage.getItem('token');
    if (token) {
      this.authService.logout(token).subscribe(
        () => {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          this.router.navigate(['/login']);
        },
        () => this.router.navigate(['/login'])
      );
    } else {
      this.router.navigate(['/login']);
    }
  }
}
