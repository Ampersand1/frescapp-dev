import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http'; // Usa HttpClientModule en lugar de provideHttpClient
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavigationBarComponent } from './components/navigation-bar/navigation-bar.component';
import { ProductsComponent } from './components/products/products.component';
import { ClientesComponent } from './components/clientes/clientes.component';
import { PurchasesComponent } from './components/purchases/purchases.component';
import { OrdenesComponent } from './components/ordenes/ordenes.component';
import { PurchaseComponent } from './components/purchases/purchase/purchase.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LoginComponent } from './components/login/login.component';
import { HomeComponent } from './components/home/home.component';
import { ReportsComponent } from './components/reports/reports.component';
import { RestorePasswordComponent } from './components/restore-password/restore-password.component';
import { DeleteAccountComponent } from './components/delete-account/delete-account.component';
import { ListActionnsCustomersComponent } from './components/crm/list-actionns-customers/list-actionns-customers.component';
import { NewActionComponent } from './components/crm/new-action/new-action.component';
import { EditActionComponent } from './components/crm/edit-action/edit-action.component';
import { NgSelectModule } from '@ng-select/ng-select';
import { CommonModule, DatePipe } from '@angular/common';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SuppliersComponent  } from './components/purchases/suppliers/suppliers.component';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { ListRutasComponent  } from './components/ruta/list-rutas/list-rutas.component';
import { StopsComponent  } from './components/ruta/stops/stops.component';
import { PricingComponent  } from './components/pricing/pricing.component';
import { CostsComponent  } from './components/costs/costs.component';
import { InventoryComponent  } from './components/inventory/inventory.component';
import { EditInventoryComponent  } from './components/inventory/edit-inventory/edit-inventory.component';
import { ProductsAnalyticsComponent } from './components/products-analytics/products-analytics.component';
import { CierresComponent } from './components/cierres/cierres/cierres.component';
import { CierreComponent } from './components/cierres/cierre/cierre.component';
import { CarteraComponent } from './components/cartera/cartera.component';
import { StrikeComponent } from './components/strikes/strike/strike.component';
import { StrikesComponent } from './components/strikes/strikes/strikes.component';
import { MoneyFormatPipe } from './money-format.pipe';
import { UeComponent } from './components/ue/ue.component'; // Importa el componente UE si es necesario
import { PedidosReportComponent } from './components/pedidos-report/pedidos-report.component'; // Importa el componente de reportes de pedidos
import { OrdenComponent } from './components/ordenes/orden/orden.component';
import { InstitucionalComponent } from './components/institucional/institucional.component';
import { NewPedidoComponent } from "./components/institucional/new-pedido/new-pedido.component"; // Importa el componente institucional
@NgModule({
  declarations: [
    MoneyFormatPipe,
    AppComponent,
    NavigationBarComponent,
    ProductsComponent,
    ClientesComponent,
    OrdenesComponent,
    LoginComponent,
    HomeComponent,
    ReportsComponent,
    RestorePasswordComponent,
    DeleteAccountComponent,
    PurchasesComponent,
    PurchaseComponent,
    ListActionnsCustomersComponent,
    NewActionComponent,
    EditActionComponent,
    SuppliersComponent,
    ListRutasComponent,
    StopsComponent,
    PricingComponent,
    CostsComponent,
    InventoryComponent,
    EditInventoryComponent,
    ProductsAnalyticsComponent,
    CierresComponent,
    CierreComponent,
    CarteraComponent,
    StrikeComponent,
    StrikesComponent,
    UeComponent,
    PedidosReportComponent,
    OrdenComponent,
    InstitucionalComponent, // Asegúrate de declarar el componente institucional aquí
  ],
  bootstrap: [AppComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    NgSelectModule,
    HttpClientModule,
    ReactiveFormsModule,
    NgbModule,
],
  providers: [DatePipe,{ provide: LocationStrategy, useClass: HashLocationStrategy }],
})
export class AppModule { }
