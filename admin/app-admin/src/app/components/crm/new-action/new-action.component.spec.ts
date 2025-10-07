import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewActionComponent } from './new-action.component';

describe('NewActionComponent', () => {
  let component: NewActionComponent;
  let fixture: ComponentFixture<NewActionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewActionComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewActionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
