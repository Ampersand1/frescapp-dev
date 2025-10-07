import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class CostsService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getCostos():Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/cost/cost');
  }
  updateCosto(costo: any) {
    return this.http.put<any>(this.baseUrl+'api/cost/cost', costo);
  }
  
  deleteCosto(cost_id: string) {
    return this.http.delete(this.baseUrl +'api/cost/cost/'+ cost_id);
  }
  createCosto(costo:any){
    return this.http.post<any>(this.baseUrl+'api/cost/cost',costo);
  }
}