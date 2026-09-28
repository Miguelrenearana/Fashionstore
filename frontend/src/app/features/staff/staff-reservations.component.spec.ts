import { TestBed } from '@angular/core/testing';

import { AuthService } from '@core/auth/auth.service';
import { StaffReservationsComponent } from './staff-reservations.component';

describe('Staff reservation transitions', () => {
  it('offers valid preparation and trial actions without direct completion', () => {
    TestBed.configureTestingModule({
      imports: [StaffReservationsComponent],
      providers: [{ provide: AuthService, useValue: { token: () => null } }],
    });
    spyOn(window, 'fetch').and.returnValue(new Promise<Response>(() => {}));

    const fixture = TestBed.createComponent(StaffReservationsComponent);
    fixture.detectChanges();
    fixture.componentInstance.reservations.set([
      { id: 1, client_id: 1, branch_id: 1, status: 'PENDING', pickup_code: 'P', expires_at: '', total_amount: 0, details: [] },
      { id: 2, client_id: 1, branch_id: 1, status: 'PREPARED', pickup_code: 'R', expires_at: '', total_amount: 0, details: [] },
      { id: 3, client_id: 1, branch_id: 1, status: 'IN_TRIAL', pickup_code: 'T', expires_at: '', total_amount: 0, details: [] },
    ]);
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Marcar preparada');
    expect(text).toContain('Iniciar prueba');
    expect(text).toContain('registra una venta vinculada');
    expect(text).not.toContain('Completar / entregar');
    expect(fixture.componentInstance.actionsFor('IN_TRIAL')).toEqual(['CANCELLED']);
  });
});
