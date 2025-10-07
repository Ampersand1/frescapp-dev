import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class InventoryService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getInventories():Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/inventory/inventories');
  }
  getInventory(close_date:any):Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/inventory/inventory/'+close_date);
  }
  updateInventory(inventory: any)  {
    return this.http.put(`${this.baseUrl}/api/inventory/inventory/${inventory.id}`, inventory);
  }

  deleteInventory(close_date: string) {
    return this.http.delete(this.baseUrl +'api/inventory/inventory/'+ close_date);
  }
  createInventory(close_date:any){
    return this.http.get<any[]>(this.baseUrl+'api/inventory/create/'+close_date);
  }
}
