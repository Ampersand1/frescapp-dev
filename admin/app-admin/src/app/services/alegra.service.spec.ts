import { TestBed } from '@angular/core/testing';

import { AlegraService } from './alegra.service';

describe('AlegraService', () => {
  let service: AlegraService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AlegraService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
