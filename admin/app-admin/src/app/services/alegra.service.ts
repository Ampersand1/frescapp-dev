import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AlegraService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://127.0.0.1:5000/';


  constructor(private http: HttpClient) { }
  send_invoice(order_number:any) {
    return this.http.get(this.baseUrl+'api/alegra/send_invoice/'+order_number);
  }
  get_invoice(order_number: any) {
    return this.http.get(this.baseUrl+'api/alegra/get_invoice/'+order_number);
  }
  send_purchase(fecha:any){
    return this.http.get(this.baseUrl+'api/alegra/send_purchase/'+fecha);
  }
}
