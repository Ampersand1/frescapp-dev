import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewPedidoComponent } from './new-pedido.component';

describe('NewPedidoComponent', () => {
  let component: NewPedidoComponent;
  let fixture: ComponentFixture<NewPedidoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewPedidoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewPedidoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
