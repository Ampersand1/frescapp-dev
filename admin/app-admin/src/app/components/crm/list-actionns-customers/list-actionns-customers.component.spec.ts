import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListActionnsCustomersComponent } from './list-actionns-customers.component';

describe('ListActionnsCustomersComponent', () => {
  let component: ListActionnsCustomersComponent;
  let fixture: ComponentFixture<ListActionnsCustomersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListActionnsCustomersComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListActionnsCustomersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
