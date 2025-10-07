import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './auth.guard';

import { ProductsComponent } from './components/products/products.component';
import { ClientesComponent } from './components/clientes/clientes.component';
import { OrdenesComponent } from './components/ordenes/ordenes.component';
import { LoginComponent } from './components/login/login.component';
import { HomeComponent } from './components/home/home.component';
import { ReportsComponent } from './components/reports/reports.component';
import { RestorePasswordComponent } from './components/restore-password/restore-password.component';
import { DeleteAccountComponent } from './components/delete-account/delete-account.component';
import { PurchasesComponent } from './components/purchases/purchases.component';
import { PurchaseComponent } from './components/purchases/purchase/purchase.component';
import { ListActionnsCustomersComponent } from './components/crm/list-actionns-customers/list-actionns-customers.component';
import { EditActionComponent } from './components/crm/edit-action/edit-action.component';
import { NewActionComponent } from './components/crm/new-action/new-action.component';
import { SuppliersComponent } from './components/purchases/suppliers/suppliers.component';
import { StopsComponent } from './components/ruta/stops/stops.component';
import { ListRutasComponent } from './components/ruta/list-rutas/list-rutas.component';
import { PricingComponent } from './components/pricing/pricing.component';
import { CostsComponent } from './components/costs/costs.component';
import { InventoryComponent } from './components/inventory/inventory.component';
import { EditInventoryComponent } from './components/inventory/edit-inventory/edit-inventory.component';
import { CierresComponent } from './components/cierres/cierres/cierres.component';
import { CierreComponent } from './components/cierres/cierre/cierre.component';
import { ProductsAnalyticsComponent } from './components/products-analytics/products-analytics.component';
import { CarteraComponent } from './components/cartera/cartera.component';
import { StrikesComponent } from './components/strikes/strikes/strikes.component';
import { StrikeComponent } from './components/strikes/strike/strike.component';
import { UeComponent } from './components/ue/ue.component';
import { PedidosReportComponent } from './components/pedidos-report/pedidos-report.component';
import { OrdenComponent } from './components/ordenes/orden/orden.component';
import { InstitucionalComponent } from './components/institucional/institucional.component';
const routes: Routes = [
  { path: 'productos', component: ProductsComponent, canActivate: [AuthGuard] },
  { path: 'clientes', component: ClientesComponent, canActivate: [AuthGuard] },
  { path: 'ordenes', component: OrdenesComponent, canActivate: [AuthGuard] },
  { path: 'home', component: HomeComponent, canActivate: [AuthGuard] },
  { path: 'reports', component: ReportsComponent, canActivate: [AuthGuard] },
  { path: 'delete-account', component: DeleteAccountComponent, canActivate: [AuthGuard] },
  { path: 'purchases', component: PurchasesComponent, canActivate: [AuthGuard] },
  { path: 'purchase/:purchaseNumber', component: PurchaseComponent, canActivate: [AuthGuard] },
  { path: 'crm', component: ListActionnsCustomersComponent, canActivate: [AuthGuard] },
  { path: 'edit_action/:action', component: EditActionComponent, canActivate: [AuthGuard] },
  { path: 'newAction', component: NewActionComponent, canActivate: [AuthGuard] },
  { path: 'suppliers', component: SuppliersComponent, canActivate: [AuthGuard] },
  { path: 'rutas', component: ListRutasComponent, canActivate: [AuthGuard] },
  { path: 'precios', component: PricingComponent, canActivate: [AuthGuard] },
  { path: 'costos', component: CostsComponent, canActivate: [AuthGuard] },
  { path: 'inventories', component: InventoryComponent, canActivate: [AuthGuard] },
  { path: 'stops/:route_number', component: StopsComponent, canActivate: [AuthGuard] },
  { path: 'inventory/:id', component: EditInventoryComponent, canActivate: [AuthGuard] },
  { path: 'products-analytics', component: ProductsAnalyticsComponent, canActivate: [AuthGuard] },
  { path: 'cierres', component: CierresComponent, canActivate: [AuthGuard] },
  { path: 'cierre/:fecha', component: CierreComponent, canActivate: [AuthGuard] },
  { path: 'cartera', component: CarteraComponent, canActivate: [AuthGuard] },
  { path: 'strikes', component: StrikesComponent, canActivate: [AuthGuard] },
  { path: 'strike/:id', component: StrikeComponent, canActivate: [AuthGuard] },
  { path: 'ue', component: UeComponent, canActivate: [AuthGuard] },
  { path: 'pedidos-report', component: PedidosReportComponent, canActivate: [AuthGuard] },
  { path: 'orden/:id', component: OrdenComponent, canActivate: [AuthGuard] },
  { path: 'institucional', component: InstitucionalComponent, canActivate: [AuthGuard] },

  // públicas
  { path: 'login', component: LoginComponent },
  { path: 'restore/:user_id', component: RestorePasswordComponent },

  // por defecto
  { path: '', redirectTo: 'home', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: false })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
