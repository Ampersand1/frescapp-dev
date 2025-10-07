import { TestBed } from '@angular/core/testing';

import { ProductsAnalyticsService } from './products-analytics.service';

describe('ProductsAnalyticsService', () => {
  let service: ProductsAnalyticsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ProductsAnalyticsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
