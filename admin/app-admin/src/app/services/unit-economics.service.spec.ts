import { TestBed } from '@angular/core/testing';

import { UnitEconomicsService } from './unit-economics.service';

describe('UnitEconomicsService', () => {
  let service: UnitEconomicsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UnitEconomicsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
