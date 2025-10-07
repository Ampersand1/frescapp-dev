import { TestBed } from '@angular/core/testing';

import { StrikesService } from './strikes.service';

describe('StrikesService', () => {
  let service: StrikesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StrikesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
