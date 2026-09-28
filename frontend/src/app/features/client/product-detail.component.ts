import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ClientService, ProductVariant, Branch } from './client.service';

interface SizeOption { name: string; variants: ProductVariant[]; }
interface ColorOption { name: string; variants: ProductVariant[]; }

@Component({
  selector: 'app-client-product-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="page" *ngIf="product; else loadingTpl">
      <a routerLink="/client/catalog" class="back-link">← Volver al catálogo</a>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      <div class="detail-grid">
        <div class="gallery card">
          @if (product.images.length > 0) {
            <img class="main-img" [src]="mainImage" [alt]="product.name" />
          } @else {
            <div class="no-img">Sin imagen</div>
          }
          <div class="thumbs" *ngIf="product.images.length > 1">
            @for (img of product.images; track img; let i = $index) {
              <button type="button" class="thumb" (click)="mainImage = img" [class.active]="mainImage === img">
                <img [src]="img" [alt]="''" />
              </button>
            }
          </div>
        </div>

        <div class="info">
          <h1 class="title">{{ product.name }}</h1>
          <p class="category">{{ product.category_name || product.brand || 'Ropa' }}</p>

          <p class="price">
            <ng-container *ngIf="product.min_price && product.base_price && product.min_price < product.base_price; else singlePrice">
              <span class="old">Bs {{ product.base_price | number:'1.2-2' }}</span>
              Bs {{ product.min_price | number:'1.2-2' }}
              <span class="disc" *ngIf="product.discount_percentage">-{{ product.discount_percentage }}%</span>
            </ng-container>
            <ng-template #singlePrice>Bs {{ product.min_price ?? product.base_price ?? product.price | number:'1.2-2' }}</ng-template>
          </p>

          @if (product.description) {
            <p class="desc">{{ product.description }}</p>
          }

          @if (variants.length > 0) {
            <div class="variants">
              <div class="field" *ngIf="sizes.length > 0">
                <label class="field-label">Talla</label>
                <select class="select" [(ngModel)]="selectedSize" (ngModelChange)="onSizeChange()">
                  <option value="">Seleccionar talla</option>
                  @for (s of sizes; track s.name) {
                    <option [value]="s.name">{{ s.name }}</option>
                  }
                </select>
              </div>
              <div class="field" *ngIf="colors.length > 0">
                <label class="field-label">Color</label>
                <select class="select" [(ngModel)]="selectedColor" (ngModelChange)="onColorChange()">
                  <option value="">Seleccionar color</option>
                  @for (c of colors; track c.name) {
                    <option [value]="c.name">{{ c.name }}</option>
                  }
                </select>
              </div>
            </div>
          }

          <div class="branch-avail card">
            <h3 class="avail-title">Disponibilidad por sucursal</h3>
            <p class="avail-hint" *ngIf="!selectedVariant">Selecciona una talla y color para consultar disponibilidad.</p>
            <ng-container *ngIf="selectedVariant">
              <select class="select w-full" [(ngModel)]="selectedBranchId" (ngModelChange)="loadBranchAvailability()">
                <option value="">Elige una sucursal...</option>
                @for (b of branches; track b.id) {
                  <option [value]="b.id">{{ b.name }}</option>
                }
              </select>

              @if (checkingStock) {
                <p class="avail-hint">Consultando disponibilidad...</p>
              } @else if (branchStock !== null) {
                <p class="branch-stock" [class.out]="branchStock <= 0">
                  {{ branchStock > 0 ? branchStock + ' unidades disponibles en esta sucursal' : 'Sin unidades disponibles en esta sucursal' }}
                </p>
              }
            </ng-container>
          </div>

          <div class="actions">
            <div class="qty">
              <label class="field-label">Cantidad</label>
              <div class="qty-control">
                <button type="button" class="qty-btn" (click)="changeQty(-1)">−</button>
                <span class="qty-value">{{ quantity }}</span>
                <button type="button" class="qty-btn" (click)="changeQty(1)">+</button>
              </div>
            </div>

            <button type="button" class="btn btn-outline" (click)="addToCart()" [disabled]="!selectedVariant">
              🛒 Agregar al carrito
            </button>
            <button type="button" class="btn btn-primary" (click)="reserve()" [disabled]="!selectedVariant">
              📦 Reservar para probar en tienda
            </button>
          </div>

          @if (actionMsg) {
            <div class="alert alert-success">{{ actionMsg }}</div>
          }
        </div>
      </div>
    </div>

    <ng-template #loadingTpl>
      <div class="loading">Cargando producto...</div>
    </ng-template>
  `,
  styles: [
    `
      .back-link { display: inline-block; margin-bottom: 1rem; color: var(--color-text-muted); text-decoration: none; }
      .back-link:hover { color: var(--color-primary, #ff8c00); }
      .detail-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 1.5rem; }
      @media (max-width: 800px) { .detail-grid { grid-template-columns: 1fr; } }
      .gallery { padding: 1rem; }
      .main-img { width: 100%; aspect-ratio: 4/5; object-fit: cover; border-radius: 10px; }
      .no-img { width: 100%; aspect-ratio: 4/5; display: flex; align-items: center; justify-content: center; color: var(--color-text-muted); }
      .thumbs { display: flex; gap: 0.5rem; margin-top: 0.75rem; overflow-x: auto; }
      .thumb { border: 2px solid transparent; border-radius: 8px; padding: 0; cursor: pointer; overflow: hidden; }
      .thumb img { width: 64px; height: 64px; object-fit: cover; display: block; }
      .thumb.active { border-color: var(--color-primary, #ff8c00); }
      .title { margin: 0 0 4px; }
      .category { color: var(--color-text-muted); margin: 0 0 0.75rem; }
      .price { font-size: 1.5rem; font-weight: 700; color: var(--color-primary, #ff8c00); margin: 0 0 0.75rem; }
      .old { text-decoration: line-through; color: var(--color-text-muted); font-weight: 400; font-size: 1rem; margin-right: 0.5rem; }
      .disc { background: var(--color-error, #ef4444); color: #fff; font-size: 0.75rem; padding: 2px 8px; border-radius: 99px; margin-left: 0.5rem; }
      .desc { color: var(--color-text); line-height: 1.5; }
      .variants { margin: 1rem 0; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
      .field { display: flex; flex-direction: column; gap: 0.3rem; }
      .field-label { font-size: 0.8rem; color: var(--color-text-muted); }
      .stock { font-weight: 600; color: var(--color-success, #16a34a); }
      .stock.out { color: var(--color-error, #ef4444); }
      .branch-avail { padding: 1rem; margin: 1rem 0; border-left: 3px solid var(--color-primary, #ff8c00); }
      .avail-title { margin: 0 0 0.5rem; font-size: 1rem; }
      .avail-hint { color: var(--color-text-muted); font-size: 0.85rem; margin: 0.5rem 0 0; }
      .branch-stock { font-weight: 600; margin: 0.5rem 0 0; color: var(--color-success, #16a34a); }
      .branch-stock.out { color: var(--color-error, #ef4444); }
      .actions { display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: flex-end; }
      .qty-control { display: flex; align-items: center; gap: 0.5rem; }
      .qty-btn { width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--color-border); background: var(--color-surface); cursor: pointer; }
      .qty-value { min-width: 24px; text-align: center; font-weight: 600; }
      .w-full { width: 100%; }
      .loading { text-align: center; color: var(--color-text-muted); padding: 4rem 0; }
    `,
  ],
})
export class ProductDetailComponent implements OnInit {
  private api = inject(ClientService);
  private route = inject(ActivatedRoute);

  product: any = null;
  variants: ProductVariant[] = [];
  sizes: SizeOption[] = [];
  colors: ColorOption[] = [];
  branches: Branch[] = [];

  selectedSize = '';
  selectedColor = '';
  selectedVariant: ProductVariant | null = null;
  quantity = 1;

  changeQty(delta: number): void {
    this.quantity = Math.max(1, this.quantity + delta);
  }
  mainImage = '';
  error = '';
  actionMsg = '';

  selectedBranchId: number | null = null;
  branchStock: number | null = null;
  checkingStock = false;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id) return;
    this.loadProduct(id);
    this.api.getBranches().subscribe({
      next: (data) => (this.branches = Array.isArray(data) ? data : (data as any).items ?? []),
      error: () => (this.branches = []),
    });
  }

  loadProduct(id: number): void {
    this.api.getProduct(id).subscribe({
      next: (res: any) => {
        const p = res.item ?? res.product ?? res.data ?? res;
        this.product = p;
        this.mainImage = p.images?.length ? (typeof p.images[0] === 'string' ? p.images[0] : p.images[0].url) : '';
        this.variants = (p.variants ?? []).map((v: any) => {
          const img = p.images?.length ? (typeof p.images[0] === 'string' ? p.images[0] : p.images[0].url) : '';
          return {
            id: v.id,
            size: v.size_name ?? v.size,
            color: v.color_name ?? v.color,
            stock: v.stock ?? v.inventory ?? (v.in_stock ? 1 : 0),
            price: v.price,
            sku: v.sku,
            in_stock: v.in_stock ?? (v.stock ?? 0) > 0,
          };
        });
        this.buildVariantOptions();
      },
      error: () => (this.error = 'No se pudo cargar el producto.'),
    });
  }

  private buildVariantOptions(): void {
    const sizeMap = new Map<string, ProductVariant[]>();
    const colorMap = new Map<string, ProductVariant[]>();
    for (const v of this.variants) {
      if (v.size) {
        if (!sizeMap.has(v.size)) sizeMap.set(v.size, []);
        sizeMap.get(v.size)!.push(v);
      }
      if (v.color) {
        if (!colorMap.has(v.color)) colorMap.set(v.color, []);
        colorMap.get(v.color)!.push(v);
      }
    }
    this.sizes = [...sizeMap.entries()].map(([name, variants]) => ({ name, variants }));
    this.colors = [...colorMap.entries()].map(([name, variants]) => ({ name, variants }));
  }

  private findVariant(): ProductVariant | null {
    return (
      this.variants.find(
        (v) => (!this.sizes.length || v.size === this.selectedSize || !this.selectedSize) &&
                   (!this.colors.length || v.color === this.selectedColor || !this.selectedColor)
      ) ?? null
    );
  }

  onSizeChange(): void {
    // Re-filter colors available for the chosen size
    if (this.selectedSize && this.colors.length > 0) {
      const variantsForSize = this.sizes.find((s) => s.name === this.selectedSize)?.variants ?? [];
      const availableColors = [...new Set(variantsForSize.map((v) => v.color).filter(Boolean))];
      this.colors = [...this.colors].filter((c) => availableColors.includes(c.name));
    }
    this.selectedVariant = this.findVariant();
    this.branchStock = null;
    this.checkingStock = false;
  }

  onColorChange(): void {
    // Re-filter sizes available for the chosen color
    if (this.selectedColor && this.sizes.length > 0) {
      const variantsForColor = this.colors.find((c) => c.name === this.selectedColor)?.variants ?? [];
      const availableSizes = [...new Set(variantsForColor.map((v) => v.size).filter(Boolean))];
      this.sizes = [...this.sizes].filter((s) => availableSizes.includes(s.name));
    }
    this.selectedVariant = this.findVariant();
    this.branchStock = null;
    this.checkingStock = false;
  }

  loadBranchAvailability(): void {
    if (!this.selectedVariant || !this.selectedBranchId) { this.branchStock = null; this.checkingStock = false; return; }
    this.checkingStock = true;
    this.branchStock = null;
    const branchId = this.selectedBranchId;
    const variantId = this.selectedVariant.id;
    this.api.getBranchAvailability(this.product.id, branchId).subscribe({
      next: (res: any) => {
        if (this.selectedBranchId !== branchId || this.selectedVariant?.id !== variantId) return;
        const p = res.item ?? res.product ?? res.data ?? res;
        const match = (p.variants ?? []).find((v: any) => v.id === variantId);
        this.branchStock = match?.available ?? 0;
        this.checkingStock = false;
      },
      error: () => {
        if (this.selectedBranchId !== branchId || this.selectedVariant?.id !== variantId) return;
        this.branchStock = null;
        this.checkingStock = false;
        this.error = 'No se pudo consultar la disponibilidad de esta sucursal.';
      },
    });
  }

  addToCart(): void {
    if (!this.selectedVariant) {
      this.error = 'Selecciona talla y color primero.';
      return;
    }
    this.error = '';
    this.api.addCartItem(this.selectedVariant.id, this.quantity).subscribe({
      next: () => { this.actionMsg = `Agregado al carrito: ${this.quantity} × ${this.product.name}`; },
      error: () => (this.error = 'No se pudo agregar al carrito.'),
    });
  }

  reserve(): void {
    if (!this.selectedVariant) {
      this.error = 'Selecciona talla y color primero.';
      return;
    }
    if (!this.selectedBranchId) {
      this.error = 'Elige una sucursal antes de reservar.';
      return;
    }
    if (this.checkingStock || this.branchStock === null) {
      this.error = 'Consulta la disponibilidad de la sucursal antes de reservar.';
      return;
    }
    if (this.branchStock < this.quantity) {
      this.error = 'No hay unidades disponibles suficientes en esta sucursal.';
      return;
    }
    this.error = '';
    this.api.createReservation([{ variant_id: this.selectedVariant.id, quantity: this.quantity }], this.selectedBranchId).subscribe({
      next: () => { this.actionMsg = '¡Reserva creada! Revisala en "Mis reservas".'; },
      error: () => (this.error = 'No se pudo crear la reserva.'),
    });
  }
}