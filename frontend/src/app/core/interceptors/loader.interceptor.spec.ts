import { TestBed } from '@angular/core/testing';

import { LoaderInterceptor } from './loader.interceptor';
import { LoaderService } from '../services/loader.service';

describe('LoaderInterceptor', () => {
  let interceptor: LoaderInterceptor;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [LoaderInterceptor, LoaderService],
    });

    interceptor = TestBed.inject(LoaderInterceptor);
  });

  it('should be created', () => {
    expect(interceptor).toBeTruthy();
  });
});
