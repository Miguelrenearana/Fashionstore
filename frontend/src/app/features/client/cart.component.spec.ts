import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { CartComponent } from './cart.component';

describe('Cart quantity updates', () => {
  it('ignores repeat clicks during PATCH and restores controls and quantity after failure', () => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    const http = TestBed.inject(HttpTestingController);
    const cart = TestBed.runInInjectionContext(() => new CartComponent());
    const item = { variant_id: 1, name: 'Shirt', price: 25, quantity: 2 };
    cart.items = [item];
    cart.changeQty(item, 3);
    expect(cart.updating.has(1)).toBeTrue();
    cart.changeQty(item, 4);
    const request = http.expectOne(r => r.url.endsWith('/cart/items/1'));
    expect(request.request.body).toEqual({ variant_id: 1, quantity: 3 });
    request.flush({}, { status: 409, statusText: 'Stock insufficient' });
    expect(item.quantity).toBe(2);
    expect(cart.updating.has(1)).toBeFalse();
    expect(cart.error).toBeTruthy();
    cart.changeQty(item, 3);
    http.expectOne(r => r.url.endsWith('/cart/items/1')).flush({});
    expect(item.quantity).toBe(3);
    expect(cart.subtotal).toBe(75);
    expect(cart.updating.size).toBe(0);
    http.verify();
  });
});
