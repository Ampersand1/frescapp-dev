import { TestBed } from '@angular/core/testing';

import { CierresService } from './cierres.service';

describe('CierresService', () => {
  let service: CierresService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CierresService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
