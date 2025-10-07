import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CierresService } from '../../../services/cierres.service';
export interface ProductSummary {
  sku: string;
  name: string;
  totalEstimated: number;
  totalReal: number;
  price_purchase?: number;
  total_quantity_ordered?: number;
  final_price_purchase?: number;
  difference?: number;
// porcentaje de diferencia sobre total real
}
interface SupplierSummary {
  supplier: string;
  totalVolume: number;   // suma de cantidades pedidas
  totalMoney: number;    // suma de price_purchase × cantidad pedida
  totalItems: number;    // número de líneas de pedido
}
interface StatusSummary {
  status: string;
  count: number;            // número de productos en ese estado
  totalVolume: number;      // suma de total_quantity_ordered
  totalMoney: number;       // suma de price_purchase × total_quantity_ordered
}
@Component({
  selector: 'app-cierre',
  templateUrl: './cierre.component.html'
})

export class CierreComponent implements OnInit {
  fechaParam!: string;
  datos_cierre: any;
  top_20_purchase: ProductSummary[] = [];
  suppliesSummary: SupplierSummary[] = [];
  purchasesByStatus: StatusSummary[] = [];
  percentByVolume?: number; // porcentaje de diferencia sobre total estimado
  percentByMoney?: number;
  totalVolume?: number; // total de volumen de productos
  totalMoney?: number;  // total de dinero de productos
  cash_margin?: number; // margen de efectivo
  cierre_total?: number; // total estimado de productos
  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private svc: CierresService
  ) { }

  ngOnInit() {
    this.fechaParam = this.route.snapshot.paramMap.get('fecha')!;
    this.svc.getCierre(this.fechaParam).subscribe(datos => {
      this.datos_cierre = datos;
      this.load_top_purchases();
      this.load_top_supplies();
      this.loadPurchasesByStatus();
    });
  }
load_top_purchases(): void {
  // 1) Agrupar en un objeto por SKU
  const summaryDict: {
    [sku: string]: Omit<ProductSummary, 'difference'>
  } = {};

  this.datos_cierre.purchase.products.forEach((item: { sku: any; price_purchase: number; total_quantity_ordered: number; final_price_purchase: number; name: any; }) => {
    const key = item.sku;
    const est = item.price_purchase * item.total_quantity_ordered;
    const real = item.final_price_purchase * item.total_quantity_ordered;

    if (!summaryDict[key]) {
      summaryDict[key] = {
        sku: item.sku,
        name: item.name,
        price_purchase: item.price_purchase,
        final_price_purchase: item.final_price_purchase,
        total_quantity_ordered: item.total_quantity_ordered,
        totalEstimated: est,
        totalReal: real
      };
    } else {
      const existing = summaryDict[key];
      existing.total_quantity_ordered = (existing.total_quantity_ordered ?? 0) + item.total_quantity_ordered;
      existing.totalEstimated          = (existing.totalEstimated ?? 0) + est;
      existing.totalReal               = (existing.totalReal ?? 0) + real;
    }
  });

  // 2) Convertir a array, calcular diferencia (estimado - real) y ordenar ascendente
  const allSummaries: ProductSummary[] = Object
    .values(summaryDict)
    .map(s => ({
      ...s,
      difference: s.totalEstimated - s.totalReal  // puede ser negativo
    }))
    .sort((a, b) => a.difference - b.difference)  // de más negativo a menos negativo
    .slice(0, 20);

  // 3) Asignar al array del componente
  this.top_20_purchase = allSummaries;
}
load_top_supplies(): void {
    // 1) Usamos un objeto para agrupar por proveedor
  const summaryDict: { [supplier: string]: SupplierSummary } = {};

  this.datos_cierre.purchase.products.forEach((item: { proveedor: { name: string; }; total_quantity_ordered: number; price_purchase: number; }) => {
    // Obtener nombre del proveedor o un placeholder
    const supplier = item.proveedor?.name ?? 'Sin proveedor';

    // Inicializar si es la primera vez que vemos el proveedor
    if (!summaryDict[supplier]) {
      summaryDict[supplier] = {
        supplier,
        totalVolume: 0,
        totalMoney: 0,
        totalItems: 0
      };
    }

    // Acumular métricas
    const summary = summaryDict[supplier];
    summary.totalVolume += item.total_quantity_ordered;
    summary.totalMoney  += item.price_purchase * item.total_quantity_ordered;
    summary.totalItems  += 1;
  });

  // 2) Convertir a arreglo y asignar a la propiedad del componente
  this.suppliesSummary = Object.values(summaryDict)
    // opcional: ordenar de mayor a menor dinero
    .sort((a, b) => b.totalMoney - a.totalMoney)
    // opcional: tomar top 20
    .slice(0, 20);
  }

loadPurchasesByStatus(): void {
  const dict: { [status: string]: StatusSummary } = {};

  this.datos_cierre.purchase.products.forEach((item: { status: string; total_quantity_ordered: any; price_purchase: number; }) => {
    const st = item.status ?? 'Sin estado';
    const volume = item.total_quantity_ordered;
    const money  = item.price_purchase * volume;

    if (!dict[st]) {
      dict[st] = { status: st, count: 0, totalVolume: 0, totalMoney: 0 };
    }

    dict[st].count       += 1;
    dict[st].totalVolume += volume;
    dict[st].totalMoney  += money;
  });

  // Resultado como arreglo
  this.purchasesByStatus = Object.values(dict)
    // opcional: ordenar por cantidad descendente
    .sort((a, b) => b.count - a.count);
}
/**
 * Calcula el porcentaje (sobre el total) de volumen y dinero
 * para los estados "facturado" y "registrado" conjuntamente.
 */
getFacturadoRegistradoPercent(): void {
  const products = this.datos_cierre.purchase.products;

  // Estados que queremos unir
  const targetStates = new Set(['Facturada', 'Registrado']);

  // 1) Totales generales
  let totalVolume = 0;
  let totalMoney = 0;

  // 2) Totales de facturado + registrado
  let frVolume = 0;
  let frMoney = 0;

  products.forEach((item: { total_quantity_ordered: any; price_purchase: number; status: string; }) => {
    const vol = item.total_quantity_ordered;
    const money = item.price_purchase * vol;

    totalVolume += vol;
    totalMoney += money;

    if (targetStates.has(item.status)) {
      frVolume += vol;
      frMoney += money;
    }
  });

  // Evitar división por cero
  const percentByVolume = totalVolume
    ? (frVolume / totalVolume) * 100
    : 0;
  const percentByMoney = totalMoney
    ? (frMoney / totalMoney) * 100
    : 0;

  this.percentByVolume = percentByVolume;
  this.percentByMoney = percentByMoney;
  };
}
