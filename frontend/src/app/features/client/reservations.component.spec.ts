import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { ReservationsComponent } from './reservations.component';
import { ReservationDetailComponent } from './reservation-detail.component';

describe('Reservation API contract', () => {
  beforeEach(() => TestBed.configureTestingModule({
    imports: [ReservationsComponent, ReservationDetailComponent],
    providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([]),
      { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => '7' } } } }],
  }));

  it('shows actual branch and amount in the list', () => {
    const http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(ReservationsComponent);
    fixture.detectChanges();
    http.expectOne(r => r.url.endsWith('/reservations/me')).flush([{
      id: 7, status: 'PREPARED', branch_name: 'Centro', total_amount: 65,
      items: [{ product_name: 'Camisa', size_name: 'M', color_name: 'Azul', quantity: 1 }],
    }]);
    fixture.detectChanges();
    const content = fixture.nativeElement.textContent;
    expect(content).toContain('Centro');
    expect(content).toContain('Preparada');
    expect(content).toContain('Camisa (M, Azul) x1');
    expect(content).toContain('Bs 65.00');
    expect(content).not.toContain('Sucursal principal');
    http.verify();
  });

  for (const status of ['PENDING', 'PREPARED', 'IN_TRIAL', 'COMPLETED', 'EXPIRED']) {
    it(`renders ${status} and permits cancellation only for active states`, () => {
      const http = TestBed.inject(HttpTestingController);
      const fixture = TestBed.createComponent(ReservationDetailComponent);
      fixture.detectChanges();
      http.expectOne(r => r.url.endsWith('/reservations/7')).flush({
        id: 7, status, branch_name: 'Norte', total_amount: 50,
        items: [{ product_name: 'Camisa', size_name: 'M', color_name: 'Azul',
          unit_price: 25, quantity: 2, available: 0 }],
      });
      fixture.detectChanges();
      const content = fixture.nativeElement.textContent;
      expect(content).toContain('Norte');
      expect(content).toContain('M');
      expect(content).toContain('Azul');
      expect(content).toContain('Bs 50.00');
      expect(fixture.componentInstance.canCancel).toBe(
        ['PENDING', 'PREPARED', 'IN_TRIAL'].includes(status));
      expect(Boolean(fixture.nativeElement.querySelector('.btn-danger'))).toBe(
        ['PENDING', 'PREPARED', 'IN_TRIAL'].includes(status));
      http.verify();
    });
  }

  it('sends cancellation only for an active reservation and reflects the API result', () => {
    const http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(ReservationDetailComponent);
    fixture.detectChanges();
    http.expectOne(r => r.url.endsWith('/reservations/7')).flush({
      id: 7, status: 'IN_TRIAL', branch_name: 'Norte', total_amount: 25, items: [],
    });
    spyOn(window, 'confirm').and.returnValue(true);
    fixture.componentInstance.cancel();
    const request = http.expectOne(r => r.url.endsWith('/reservations/7/status'));
    expect(request.request.body).toEqual({ status: 'cancelled' });
    request.flush({ status: 'CANCELLED' });
    fixture.detectChanges();
    expect(fixture.componentInstance.reservation.status).toBe('CANCELLED');
    expect(fixture.nativeElement.querySelector('.btn-danger')).toBeNull();
    http.verify();
  });
});
