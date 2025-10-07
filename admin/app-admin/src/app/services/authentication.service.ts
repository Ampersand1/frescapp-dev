import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  private _username: string = '';
  constructor(private http: HttpClient) { }

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(this.baseUrl + 'api/user/login_admin', { 'user': username, 'password': password })
      .pipe(
        // Al recibir la respuesta del servidor, guardar el token en el almacenamiento local
        map(response => {
          if (response.token) {
            localStorage.setItem('token', response.token);
            localStorage.setItem('role', response.user_data.role);
          }
          return response;
        })
      );
  }

  logout(token: string): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    };
    return this.http.post<any>(this.baseUrl+'api/user/logout', {}, httpOptions);
  }

  checkToken(token: string): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    };
    return this.http.post<any>(this.baseUrl+'api/user/check_token', {}, httpOptions);
  }

  changePassword(user_id: string, newPassword: string): Observable<any> {
    return this.http.post<any>(this.baseUrl+'api/user/restore', { password: newPassword, user_id : user_id });
  }
  deleteAccount(user_email: string, password: string): Observable<any> {
    return this.http.post<any>(this.baseUrl+'api/user/delete_account', { password: password, user_email : user_email });
  }
  setUsername(username: string) {
    this._username = username;
  }

  getUsername(): string {
    return this._username;
  }
}
