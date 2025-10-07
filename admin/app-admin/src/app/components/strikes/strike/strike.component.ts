// src/app/strike/strike.component.ts

import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { StrikesService, Strike } from '../../../services/strikes.service';
import { OrderService } from '../../../services/order.service';
import { Router, ActivatedRoute } from '@angular/router';
import { startOfToday } from 'date-fns';

@Component({
  selector: 'app-strike',
  templateUrl: './strike.component.html',
  styleUrls: ['./strike.component.css']
})
export class StrikeComponent implements OnInit {
  form!: FormGroup;
  orders: any[] = [];
  items: any[] = [];
  strikeTypes = [
    { value: 'quality', label: 'Calidad' },
    { value: 'partial_missing', label: 'Faltante parcial' },
    { value: 'total_missing', label: 'Faltante total' },
    { value: 'late_arrival', label: 'Llegada tarde' },
    { value: 'cancel_order', label: 'Cancelación' }
  ];
  private strikeId?: string;

  constructor(
    private fb: FormBuilder,
    private strikeService: StrikesService,
    private orderService: OrderService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Inicializar formulario
    this.form = this.fb.group({
      order_number: [null, Validators.required],
      strike_type: [null, Validators.required],
      sku: [null],
      name: [null], // Nombre del producto, opcional si es strike de todo el pedido
      missing_quantity: [0],
      detail: ['']
    });

    // Cargar órdenes de hoy y luego precargar si hay id
    const today = startOfToday().toISOString().slice(0, 10);
    this.orderService.getOrders(today, today).subscribe(ords => {
      this.orders = ords;

      if (this.route.snapshot.paramMap.get('id') == 'new'){
        this.strikeId = ''
      }else {
      this.strikeId = this.route.snapshot.paramMap.get('id') || undefined;
      }
      if (this.strikeId) {
        this.strikeService.get(this.strikeId).subscribe((s: Strike) => {
          // Patch de valores
          this.form.patchValue({
            order_number: s.order_number,
            strike_type: s.strike_type,
            sku: s.sku,
            name: s.name, // Asegurarse de incluir el nombre del producto
            missing_quantity: s.missing_quantity,
            detail: s.detail
          });

          // Cargar items de la orden para el dropdown
          const order = this.orders.find(o => o.order_number === s.order_number);
          this.items = order ? order.products : [];
      this.form.get('sku')!.setValue(s.sku);
      this.form.get('missing_quantity')!.setValue(s.missing_quantity);
      this.onTypeChange(s.strike_type);

        });
      }
    });

    // Cuando cambie la orden, recargar items
    this.form.get('order_number')!.valueChanges.subscribe(() => this.onOrderChange());

    // Adaptar validaciones según tipo de strike
    this.form.get('strike_type')!.valueChanges.subscribe(type => this.onTypeChange(type));
  }

  onOrderChange(): void {
    const orderNum = this.form.get('order_number')!.value;
    const order = this.orders.find(o => o.order_number === orderNum);
    this.items = order ? order.products : [];
    // reset campos de producto si fue otro order
    this.form.patchValue({ sku: null, missingQuantity: 0 });
  }

  onTypeChange(type: string): void {
    const skuCtrl = this.form.get('sku')!;
    const qtyCtrl = this.form.get('missing_quantity')!;

    if (['quality', 'partial_missing', 'total_missing'].includes(type)) {
      skuCtrl.setValidators(Validators.required);
      if (type === 'partial_missing') {
        qtyCtrl.setValidators([
          Validators.required,
          Validators.min(1),
          Validators.max(this.maxQuantity())
        ]);
      } else {
        qtyCtrl.clearValidators();
        qtyCtrl.setValue(type === 'total_missing' ? this.maxQuantity() : 0);
      }
    } else {
      skuCtrl.clearValidators();
      qtyCtrl.clearValidators();
      this.form.patchValue({ sku: null, missingQuantity: 0 });
    }
    skuCtrl.updateValueAndValidity();
    qtyCtrl.updateValueAndValidity();
  }

  maxQuantity(): number {
    const sku = this.form.get('sku')!.value;
    const item = this.items.find(i => i.sku === sku);
    return item ? item.quantity : 0;
  }

  onSkuChange(): void {
    const item = this.items.find(i => i.sku ===  this.form.get('sku')!.value);
    const qtyCtrl = item.quantity;
    const v = this.form.value;
    this.form.patchValue({
      order_number: v.order_number,
      strike_type: v.strike_type,
      sku: v.sku,
      name: v.name || item.name, // Asignar nombre del producto
      missing_quantity: qtyCtrl,
      detail: v.detail
    });
  }

  submit(): void {
    const v = this.form.value;
    const payload: Partial<Strike> = {
      order_number: v.order_number,
      strike_type: v.strike_type,
      sku: v.sku,
      name: v.name, // Asegurarse de incluir el nombre del producto
      missing_quantity: v.missing_quantity,
      detail: v.detail
    };
    if (this.route.snapshot.paramMap.get('id') == 'new') {
      this.strikeId = '';
    }

    if (this.route.snapshot.paramMap.get('id') != 'new') {
      this.strikeService.update(this.route.snapshot.paramMap.get('id') || '', payload).subscribe(() => {
        this.router.navigate(['/strikes']);
      });
    } else {
      this.strikeService.create(payload as Strike).subscribe(() => {
        this.router.navigate(['/strikes']);
      });
    }
  }
}
