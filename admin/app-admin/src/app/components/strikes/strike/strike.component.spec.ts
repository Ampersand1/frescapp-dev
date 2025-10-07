import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StrikeComponent } from './strike.component';

describe('StrikeComponent', () => {
  let component: StrikeComponent;
  let fixture: ComponentFixture<StrikeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StrikeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StrikeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
