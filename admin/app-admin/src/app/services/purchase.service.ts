import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PurchaseService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getPurchases():Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/purchase/purchases/');
  }
  getPurchase(purchaseNumber:any):Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/purchase/purchase/'+purchaseNumber);
  }
  updatePurchase(purchase: any)  {
    return this.http.put(this.baseUrl +'api/purchase/purchase',purchase);
  }

  deletePurchase(purchase_number: string) {
    return this.http.delete(this.baseUrl +'api/purchase/purchase/'+ purchase_number);
  }
  createPurchase(purchase:any){
    return this.http.post<any[]>(this.baseUrl+'api/purchase/create/', purchase);
  }
  updatePrice(data:any): Observable<any[]> {
    return this.http.post<any[]>(`${this.baseUrl}api/purchase/update_price`, data);
  }
  getReport(purchase_number: string){
    return `${this.baseUrl}api/purchase/purchase/report/${purchase_number}`;
  }
  getDetailPurchase(purchase_number: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}api/purchase/purchase/detail/${purchase_number}`);
  }
  deleteProductFromPurchase(purchase_number: string, sku: string): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}api/purchase/purchase/${purchase_number}/remove-product/${sku}`);
  }
}
