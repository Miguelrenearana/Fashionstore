import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { RegisterComponent } from './register.component';

describe('Client registration errors', () => {
  beforeEach(() => TestBed.configureTestingModule({
    imports: [RegisterComponent],
    providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
  }));

  function submitValidRegistration() {
    const fixture = TestBed.createComponent(RegisterComponent);
    const component = fixture.componentInstance;
    component.first_name = 'Mario';
    component.last_name = 'Perez';
    component.email = 'new-client@example.test';
    component.password = 'test-only-password';
    fixture.detectChanges();
    component.onSubmit();
    return fixture;
  }

  it('explains a blocked connection instead of reporting a generic registration failure', () => {
    const fixture = submitValidRegistration();
    const http = TestBed.inject(HttpTestingController);
    const request = http.expectOne(r => r.url.endsWith('/auth/register'));
    expect(request.request.method).toBe('POST');
    request.error(new ProgressEvent('error'), { status: 0, statusText: 'Unknown Error' });

    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No se pudo conectar con el servidor');
    expect(fixture.componentInstance.loading).toBeFalse();
    http.verify();
  });

  it('explains when the email is already registered', () => {
    const fixture = submitValidRegistration();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne(r => r.url.endsWith('/auth/register')).flush(
      { code: 'forbidden', message: 'Email is already registered.' },
      { status: 403, statusText: 'Forbidden' },
    );

    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Este correo ya está registrado');
    expect(fixture.componentInstance.loading).toBeFalse();
    http.verify();
  });
});
