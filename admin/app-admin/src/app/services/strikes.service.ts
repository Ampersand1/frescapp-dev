import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Strike {
  id?: string;
  order_number: number;
  sku?: string;
  name?: string; // Nombre del producto, opcional si es strike de todo el pedido
  strike_type: string;
  missing_quantity: number;
  detail: string;
  timestamp?: string;
}
@Injectable({
  providedIn: 'root'
})
export class StrikesService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/api/strikes';
  //private baseUrl = 'http://localhost:5000/api/strikes';

  constructor(private http: HttpClient) { }

  /** Obtener todos los strikes */
  getAll(limit?: number): Observable<Strike[]> {
    let params = new HttpParams();
    if (limit != null) {
      params = params.set('limit', limit.toString());
    }
    return this.http.get<Strike[]>(this.baseUrl, { params });
  }

  /** Obtener strikes filtrando por número de orden */
  getByOrder(orderNumber: number): Observable<Strike[]> {
    const params = new HttpParams().set('order_number', orderNumber.toString());
    return this.http.get<Strike[]>(this.baseUrl, { params });
  }

  /** Obtener un strike por su id */
  get(id: string): Observable<Strike> {
    return this.http.get<Strike>(`${this.baseUrl}/${id}`);
  }

  /** Crear un nuevo strike */
  create(strike: Strike): Observable<{ id: string }> {
    // transformar camelCase a snake_case si es necesario en backend
    const payload = {
      order_number: strike.order_number,
      sku: strike.sku,
      strike_type: strike.strike_type,
      name: strike.name,
      missing_quantity: strike.missing_quantity,
      detail: strike.detail
    };
    return this.http.post<{ id: string }>(this.baseUrl, payload);
  }

  /** Actualizar un strike existente */
  update(id: string, strike: Partial<Strike>): Observable<any> {
    const payload: any = {};
    if (strike.order_number    != null) payload.order_number    = strike.order_number;
    if (strike.sku            != null) payload.sku             = strike.sku;
    if (strike.name           != null) payload.name            = strike.name;
    if (strike.strike_type     != null) payload.strike_type     = strike.strike_type;
    if (strike.missing_quantity!= null) payload.missing_quantity= strike.missing_quantity;
    if (strike.detail         != null) payload.detail          = strike.detail;
    return this.http.put(`${this.baseUrl}/${id}`, payload);
  }

  /** Eliminar un strike */
  delete(id: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${id}`);
  }
}
