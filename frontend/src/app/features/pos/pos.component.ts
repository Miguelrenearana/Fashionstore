import { Component } from '@angular/core';

@Component({
  selector: 'app-pos',
  standalone: true,
  template: `
    <section class="pos">
      <h2>Punto de Venta</h2>

      <div class="card p-4 mb-4">
        <h3 class="text-lg font-semibold mb-3">Nueva venta</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
          <div>
            <label class="form-label text-sm block mb-1">Código prenda</label>
            <input type="text" class="form-input" placeholder="V1234" />
          </div>
          <div>
            <label class="form-label text-sm block mb-1">Cantidad</label>
            <input type="number" class="form-input" value="1" min="1" />
          </div>
        </div>
        <button class="btn btn-primary w-full">Agregar al carrito</button>
      </div>

      <div class="grid grid-cols-1 gap-3">
        <div class="card p-3">
          <h4 class="text-sm font-medium mb-2">Carrito</h4>
          <p>0 items - $0.00</p>
        </div>
        <div class="card p-3">
          <h4 class="text-sm font-medium mb-2">Total</h4>
          <p class="text-xl font-bold">$0.00</p>
        </div>
      </div>

      <div class="mt-4">
        <button class="btn btn-block btn-lg btn-primary">Finalizar compra</button>
      </div>
    </section>
  `,
  styles: []
})
export class PosComponent {}