import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SupplierService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getSuppliers():Observable<any> {
    return this.http.get(`${this.baseUrl}api/supplier/suppliers`);
  }

  createSupplier(supplier: any):Observable<any> {
    return this.http.post(`${this.baseUrl}api/supplier/supplier`, supplier);
  }

  updateSupplier(supplier: any):Observable<any> {
    return this.http.put(`${this.baseUrl}api/supplier/supplier/${supplier._id}`, supplier);
  }

  deleteSupplier(supplierId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/supplier/supplier/${supplierId}`);
  }
}
