import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StrikesComponent } from './strikes.component';

describe('StrikesComponent', () => {
  let component: StrikesComponent;
  let fixture: ComponentFixture<StrikesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StrikesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StrikesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
