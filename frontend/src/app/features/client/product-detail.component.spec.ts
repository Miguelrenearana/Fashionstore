import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { ProductDetailComponent } from './product-detail.component';

describe('Product detail availability and reservation', () => {
  beforeEach(() => TestBed.configureTestingModule({
    imports: [ProductDetailComponent],
    providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([]),
      { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => '5' } } } }],
  }));

  it('uses available for the selected variant and branch, and requires a branch to reserve', () => {
    const http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(ProductDetailComponent);
    fixture.detectChanges();
    http.expectOne(r => r.url.endsWith('/catalog/5') && !r.params.has('branch_id')).flush({
      id: 5, name: 'Camisa', images: [], variants: [
        { id: 11, size_name: 'M', color_name: 'Azul', stock: 1, available: 1, price: 25 },
      ],
    });
    http.expectOne(r => r.url.endsWith('/locations/branches')).flush([{ id: 2, name: 'Centro' }]);
    const detail = fixture.componentInstance;
    detail.selectedSize = 'M';
    detail.selectedColor = 'Azul';
    detail.onSizeChange();
    detail.reserve();
    expect(detail.error).toContain('Elige una sucursal');
    http.expectNone(r => r.url.endsWith('/reservations'));

    detail.selectedBranchId = 2;
    detail.loadBranchAvailability();
    http.expectOne(r => r.url.endsWith('/catalog/5') && r.params.get('branch_id') === '2').flush({
      variants: [{ id: 11, size_name: 'M', color_name: 'Azul', stock: 1, available: 0 }],
    });
    fixture.detectChanges();
    expect(detail.branchStock).toBe(0);
    expect(fixture.nativeElement.textContent).toContain('Sin unidades disponibles');
    detail.reserve();
    expect(detail.error).toContain('No hay unidades disponibles');
    http.expectNone(r => r.url.endsWith('/reservations'));

    detail.loadBranchAvailability();
    http.expectOne(r => r.url.endsWith('/catalog/5') && r.params.get('branch_id') === '2').flush({
      variants: [{ id: 11, stock: 2, available: 1 }],
    });
    detail.reserve();
    const request = http.expectOne(r => r.url.endsWith('/reservations'));
    expect(request.request.body).toEqual({ items: [{ variant_id: 11, quantity: 1 }], branch_id: 2 });
    request.flush({ id: 3 });
    http.verify();
  });
});
