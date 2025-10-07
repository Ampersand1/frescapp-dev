import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CierresComponent } from './cierres.component';

describe('CierresComponent', () => {
  let component: CierresComponent;
  let fixture: ComponentFixture<CierresComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CierresComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CierresComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
