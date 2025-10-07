import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class ProductHistoryService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';

  constructor(private httpClient: HttpClient) { }

  getProductsHistory(operation_date_start:any,operation_date_end:any): Observable<any[]> {
    return this.httpClient.get<any[]>(this.baseUrl+'api/products_history/products_history/'+operation_date_start+'/'+operation_date_end);
  }
  updatePrices(operation_date:any): Observable<any[]> {
    return this.httpClient.get<any[]>(this.baseUrl+'api/products_history/products_history_new/'+operation_date);
  }
}
