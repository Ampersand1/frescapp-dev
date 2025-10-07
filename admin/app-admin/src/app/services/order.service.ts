import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
 private baseUrl = 'https://app.buyfrescapp.com:5000/';
 //private baseUrl = 'http://localhost:5000/';

  constructor(private http: HttpClient) { }

  getOrders(startDate:any,endDate:any): Observable<any[]> {
    return this.http.get<any[]>(this.baseUrl+'api/order/orders/'+startDate+'/'+endDate);
  }
  getOrdersByStatus(status:any): Observable<any[]> {
    return this.http.get<any[]>(this.baseUrl+'api/order/orders/status/'+status);
  }
  updateOrder(orderId: number, orderData: any): Observable<any> {
    const url = this.baseUrl + 'api/order/order/' + orderId;
    return this.http.post(url, orderData);
  }

  createOrder(orderData: any): Observable<any> {
    return this.http.post(this.baseUrl+'api/order/order', orderData);
  }
  getConfig(): Observable<any> {
      return this.http.get<any>(this.baseUrl+ 'api/config/configOrder');
  }
  deleteOrder(orderId: number){
    const url = this.baseUrl + 'api/order/order/' + orderId;
    return this.http.delete(url);
  }
  getLastOrdersByCustomerId(customerEmail:string): Observable<any> {
    return this.http.get<any>(this.baseUrl+ 'api/order/orders_latest_customer/'+customerEmail);
  }
  createOrderFromFile(file: File | null, orderData: any): Observable<any> {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    formData.append('data', JSON.stringify(orderData));
    return this.http.post(this.baseUrl + 'api/order/order/order_file', formData);
  }
}
