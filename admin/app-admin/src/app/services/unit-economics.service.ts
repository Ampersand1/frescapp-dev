import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UnitEconomicsService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getUE(tipo:any):Observable<any> {
    return this.http.get(`${this.baseUrl}api/ue/ue/${tipo}`);
  }

  updateUE(ueDate:any):Observable<any> {
    return this.http.post(`${this.baseUrl}api/ue/updateUE`,{"dateUpdate" : ueDate});
  }
  getUnitEconomics(): Observable<any> {
    return this.http.get(`${this.baseUrl}api/analytics/ue_daily`);
  }

}
