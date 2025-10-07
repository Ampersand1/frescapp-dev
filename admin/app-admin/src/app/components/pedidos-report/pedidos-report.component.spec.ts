import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PedidosReportComponent } from './pedidos-report.component';

describe('PedidosReportComponent', () => {
  let component: PedidosReportComponent;
  let fixture: ComponentFixture<PedidosReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PedidosReportComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PedidosReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
