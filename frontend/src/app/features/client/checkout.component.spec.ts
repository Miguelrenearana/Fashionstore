import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { CheckoutComponent } from './checkout.component';

describe('Mock checkout', () => {
  let http: HttpTestingController;
  let component: CheckoutComponent;
  const storageKey = 'fs-checkout-payment:901';
  const purchase = {
    sale: { id: 42, status: 'PENDING', invoice_number: 'TEST-42', total_amount: 50 },
    payment: { id: 8, sale_id: 42, gateway_reference: 'mock_test', status: 'PENDING' },
  };

  function initialize(gateway = 'mock'): CheckoutComponent {
    const checkout = TestBed.runInInjectionContext(() => new CheckoutComponent());
    checkout.ngOnInit();
    http.expectOne(r => r.url.endsWith('/payments/config')).flush({ gateway });
    http.expectOne(r => r.url.endsWith('/users/me')).flush({ id: 901 });
    http.expectOne(r => r.url.endsWith('/cart')).flush({ total: 50, details: [
      { variant_id: 1, garment_name: 'Shirt', unit_price: 25, quantity: 2 },
    ] });
    checkout.name = 'Test';
    checkout.pickup = true;
    return checkout;
  }

  function createSale(): void {
    component.placeOrder();
    const request = http.expectOne(r => r.url.endsWith('/cart/purchase'));
    expect(request.request.method).toBe('POST');
    request.flush(purchase);
  }

  function confirmation() {
    const request = http.expectOne(r => r.url.endsWith('/payments/confirm'));
    expect(request.request.body).toEqual({ gateway_reference: 'mock_test' });
    return request;
  }

  beforeEach(() => {
    sessionStorage.removeItem(storageKey);
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    http = TestBed.inject(HttpTestingController);
    component = initialize();
  });

  afterEach(() => {
    http.verify();
    sessionStorage.removeItem(storageKey);
  });

  it('shows success only after confirmation COMPLETED, not after purchase', () => {
    createSale();
    expect(component.success).toBeFalse();
    expect(component.payment?.reference).toBe('mock_test');
    confirmation().flush({ reference: 'mock_test', status: 'COMPLETED' });
    expect(component.success).toBeTrue();
    expect(sessionStorage.getItem(storageKey)).toBeNull();
  });

  for (const status of ['PENDING', 'DECLINED', 'TIMEOUT']) {
    it(`retains ${status} and retries the same reference without another sale`, () => {
      createSale();
      confirmation().flush({ reference: 'mock_test', status });
      expect(component.success).toBeFalse();
      expect(component.payment?.status).toBe(status);
      component.placeOrder();
      http.expectNone(r => r.url.endsWith('/cart/purchase'));
      confirmation().flush({ reference: 'mock_test', status });
      expect(component.payment?.saleId).toBe(42);
    });
  }

  it('recovers the reference after an error and a page reload', () => {
    createSale();
    confirmation().flush({}, { status: 503, statusText: 'Unavailable' });
    expect(component.success).toBeFalse();
    expect(component.error).toContain('último estado conocido');
    component = initialize();
    expect(component.payment?.reference).toBe('mock_test');
    component.confirmPayment();
    http.expectNone(r => r.url.endsWith('/cart/purchase'));
    confirmation().flush({ reference: 'mock_test', status: 'COMPLETED' });
    expect(component.success).toBeTrue();
  });

  it('does not duplicate requests on repeated clicks', () => {
    component.placeOrder();
    component.placeOrder();
    http.expectOne(r => r.url.endsWith('/cart/purchase')).flush(purchase);
    component.confirmPayment();
    confirmation().flush({ reference: 'mock_test', status: 'PENDING' });
  });

  it('blocks a new purchase after a lost purchase response, including after reload', () => {
    component.placeOrder();
    http.expectOne(r => r.url.endsWith('/cart/purchase')).error(new ProgressEvent('error'));
    component = initialize();
    component.placeOrder();
    http.expectNone(r => r.url.endsWith('/cart/purchase'));
    http.expectNone(r => r.url.endsWith('/payments/confirm'));
    http.expectOne(r => r.url.includes('/cart/purchase/')).flush(purchase);
    confirmation().flush({ reference: 'mock_test', status: 'COMPLETED' });
    expect(component.payment?.saleId).toBe(42);
    expect(component.success).toBeTrue();
  });

  it('allows correction after validation fails without persisting an unknown payment', () => {
    component.placeOrder();
    expect(component.payment).toBeNull();
    http.expectOne(r => r.url.endsWith('/cart/purchase')).flush({}, { status: 422, statusText: 'Invalid stock' });
    expect(sessionStorage.getItem(storageKey)).toBeNull();
    expect(component.attempt).toBeNull();
    createSale();
    confirmation().flush({ reference: 'mock_test', status: 'COMPLETED' });
    expect(component.success).toBeTrue();
  });

  it('retries an uncertain purchase with the original token when lookup returns 404', () => {
    component.placeOrder();
    const first = http.expectOne(r => r.url.endsWith('/cart/purchase'));
    const token = first.request.body.checkout_token;
    first.error(new ProgressEvent('error'));
    component.recoverPurchase();
    http.expectOne(r => r.url.endsWith('/cart/purchase/' + token)).flush({}, { status: 404, statusText: 'Not found' });
    component.submitPurchase();
    const retry = http.expectOne(r => r.url.endsWith('/cart/purchase'));
    expect(retry.request.body.checkout_token).toBe(token);
    retry.flush(purchase);
    confirmation().flush({ reference: 'mock_test', status: 'PENDING' });
    expect(component.success).toBeFalse();
  });

  it('retains the uncertain attempt after TIMEOUT instead of starting another purchase', () => {
    createSale();
    confirmation().flush({ reference: 'mock_test', status: 'TIMEOUT' });
    const token = component.attempt!.token;
    component.startNewPurchase();
    expect(component.attempt!.token).toBe(token);
    expect(component.payment?.reference).toBe('mock_test');
    http.expectNone(r => r.url.endsWith('/cart/purchase'));
    component.confirmPayment();
    confirmation().flush({ reference: 'mock_test', status: 'COMPLETED' });
    expect(component.success).toBeTrue();
  });

  for (const status of ['DECLINED']) {
    it(`allows a fresh cart after rechecking ${status}`, () => {
      createSale();
      confirmation().flush({ reference: 'mock_test', status });
      const oldToken = component.attempt!.token;
      component.startNewPurchase();
      confirmation().flush({ reference: 'mock_test', status });
      http.expectOne(r => r.url.endsWith('/cart')).flush({ details: [{ variant_id: 1, unit_price: 25, quantity: 1 }], total: 25 });
      expect(component.payment).toBeNull();
      component.placeOrder();
      const request = http.expectOne(r => r.url.endsWith('/cart/purchase'));
      expect(request.request.body.checkout_token).not.toBe(oldToken);
      request.flush({ ...purchase, sale: { ...purchase.sale, id: 43 } });
      confirmation().flush({ reference: 'mock_test', status: 'PENDING' });
      expect(component.payment?.saleId).toBe(43);
    });
  }

  it('does not create or confirm a payment for a different gateway', () => {
    component = initialize('static_qr');
    component.placeOrder();
    http.expectNone(r => r.url.endsWith('/cart/purchase'));
    http.expectNone(r => r.url.endsWith('/payments/confirm'));
    expect(component.error).toContain('mock');
  });

  it('does not trust a confirmation for a different reference', () => {
    createSale();
    confirmation().flush({ reference: 'another-payment', status: 'COMPLETED' });
    expect(component.success).toBeFalse();
    expect(component.payment?.reference).toBe('mock_test');
    expect(component.error).toContain('no corresponde');
  });
});
