import { TestBed } from '@angular/core/testing';

import { Coach } from './coach';

describe('Coach', () => {
  let service: Coach;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Coach);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
