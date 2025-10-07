import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ActionService {
   private baseUrl = 'https://app.buyfrescapp.com:5000/';
   //private baseUrl = 'http://127.0.0.1:5000/';

  constructor(private http: HttpClient) { }

  // Crear una nueva acción
  createAction(newAction: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}api/action/action`, newAction);
  }

  // Obtener todas las acciones
  getActions(date:any): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}api/action/actions/${date}`);
  }

  // Obtener una acción específica por número
  getAction(actionNumber: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}api/action/action/${actionNumber}`);
  }

  // Editar una acción existente
  editAction(actionNumber: string, updatedAction: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}api/action/action/${actionNumber}`, updatedAction);
  }

  // Eliminar una acción por número
  deleteAction(actionNumber: string): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}api/action/action/${actionNumber}`);
  }
  getPotentialCustomers(): Observable<Object[]> {
    return this.http.get<Object[]>(`${this.baseUrl}api/action/potentialCustomers`);
  }
}
