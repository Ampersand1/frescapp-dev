import { TestBed } from '@angular/core/testing';

import { WooService } from './woo.service';

describe('WooService', () => {
  let service: WooService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(WooService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
