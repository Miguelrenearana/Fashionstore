import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ClientService, CatalogItem, Category } from './client.service';

@Component({
  selector: 'app-client-catalog',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="page">
      <h1 class="page-title">Catálogo</h1>
      <p class="page-subtitle">Explora las prendas disponibles en FashionStore.</p>

      <div class="toolbar card">
        <div class="toolbar-row">
          <input
            type="search"
            class="input"
            placeholder="Buscar por nombre, marca o descripción..."
            [(ngModel)]="searchTerm"
            (keyup.enter)="applySearch()"
          />
          <button type="button" class="btn btn-primary" (click)="applySearch()">Buscar</button>
          <button type="button" class="btn btn-ghost" (click)="resetFilters()">Limpiar</button>
        </div>

        <div class="toolbar-row toolbar-filters">
          <select class="select" [(ngModel)]="selectedCategory" (ngModelChange)="loadCatalog()">
            <option value="">Todas las categorías</option>
            @for (cat of categories; track cat.id) {
              <option [value]="cat.id">{{ cat.name }}</option>
            }
          </select>

          <select class="select" [(ngModel)]="selectedBranch" (ngModelChange)="loadCatalog()">
            <option value="">Todas las sucursales</option>
            @for (branch of branches; track branch.id) {
              <option [value]="branch.id">{{ branch.name }}</option>
            }
          </select>

          <select class="select" [(ngModel)]="sortBy" (ngModelChange)="loadCatalog()">
            <option value="">Ordenar por</option>
            <option value="price_asc">Precio: menor a mayor</option>
            <option value="price_desc">Precio: mayor a menor</option>
            <option value="name">Nombre A-Z</option>
          </select>
        </div>
      </div>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (loading) {
        <div class="loading">Cargando catálogo...</div>
      } @else if (items.length === 0) {
        <div class="empty card">
          <p>No se encontraron prendas con los filtros seleccionados.</p>
        </div>
      } @else {
        <div class="grid">
          @for (item of items; track item.id) {
            <a class="product-card card" [routerLink]="['/client/catalog', item.id]">
              <div class="thumb">
                @if (item.images.length > 0) {
                  <img [src]="item.images[0]" [alt]="item.name" />
                } @else {
                  <span class="no-img">Sin imagen</span>
                }
                @if (item.is_featured || item.is_best_seller) {
                  <span class="tag">{{ item.is_best_seller ? 'Best seller' : 'Destacado' }}</span>
                }
              </div>
              <div class="card-body">
                <h3 class="card-name">{{ item.name }}</h3>
                <p class="card-category">{{ item.category_name || item.brand || 'Ropa' }}</p>
                <p class="card-price">S/{{ item.min_price ?? item.base_price ?? item.price | number: '1.2-2' }}</p>
              </div>
            </a>
          }
        </div>

        @if (totalPages > 1) {
          <div class="pagination">
            <button type="button" class="btn btn-outline" [disabled]="page <= 1" (click)="setPage(page - 1)">Anterior</button>
            <span class="page-info">Página {{ page }} de {{ totalPages }} · {{ total }} prendas</span>
            <button type="button" class="btn btn-outline" [disabled]="page >= totalPages" (click)="setPage(page + 1)">Siguiente</button>
          </div>
        }
      }
    </div>
  `,
  styles: [
    `
      .page-title { margin-bottom: 4px; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .toolbar { padding: 1rem; margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; }
      .toolbar-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
      .input { flex: 1; min-width: 220px; }
      .toolbar-filters { gap: 0.75rem; }
      .select { min-width: 180px; }
      .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 1rem; }
      .product-card { text-decoration: none; color: inherit; display: block; overflow: hidden; transition: transform 0.15s, box-shadow 0.15s; }
      .product-card:hover { transform: translateY(-3px); box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1); }
      .thumb { height: 180px; background: var(--color-surface-variant, #f3f4f6); position: relative; overflow: hidden; }
      .thumb img { width: 100%; height: 100%; object-fit: cover; }
      .no-img { display: flex; align-items: center; justify-content: center; height: 100%; color: var(--color-text-muted); font-size: 0.85rem; }
      .tag { position: absolute; top: 8px; left: 8px; background: var(--color-primary, #ff8c00); color: #fff; font-size: 0.7rem; padding: 2px 8px; border-radius: 99px; }
      .card-body { padding: 0.75rem 1rem; }
      .card-name { font-size: 0.95rem; margin: 0 0 2px; }
      .card-category { font-size: 0.78rem; color: var(--color-text-muted); margin: 0 0 6px; }
      .card-price { font-weight: 600; color: var(--color-primary, #ff8c00); margin: 0; }
      .pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1.5rem; }
      .page-info { color: var(--color-text-muted); font-size: 0.9rem; }
      .loading { text-align: center; color: var(--color-text-muted); padding: 3rem 0; }
      .empty { text-align: center; color: var(--color-text-muted); padding: 3rem 0; }
    `,
  ],
})
export class CatalogComponent implements OnInit {
  private api = inject(ClientService);

  items: CatalogItem[] = [];
  categories: Category[] = [];
  branches: any[] = [];

  searchTerm = '';
  selectedCategory: string = '';
  selectedBranch: string = '';
  sortBy = '';

  page = 1;
  size = 12;
  total = 0;
  totalPages = 1;
  loading = false;
  error = '';

  ngOnInit(): void {
    this.loadCategories();
    this.loadBranches();
    this.loadCatalog();
  }

  loadCategories(): void {
    this.api.getCategories().subscribe({
      next: (data) => (this.categories = data),
      error: () => (this.categories = []),
    });
  }

  loadBranches(): void {
    this.api.getBranches().subscribe({
      next: (data) => (this.branches = Array.isArray(data) ? data : (data as any).items ?? []),
      error: () => (this.branches = []),
    });
  }

  loadCatalog(): void {
    this.loading = true;
    this.error = '';
    this.api
      .getCatalog({
        page: this.page,
        size: this.size,
        search: this.searchTerm || undefined,
        category_id: this.selectedCategory ? Number(this.selectedCategory) : undefined,
        branch_id: this.selectedBranch ? Number(this.selectedBranch) : undefined,
        sort_by: this.sortBy || undefined,
      })
      .subscribe({
        next: (res: any) => {
          this.items = res.items ?? res.data ?? (Array.isArray(res) ? res : []);
          this.total = res.total ?? this.items.length;
          this.totalPages = res.pages ?? res.total_pages ?? 1;
          this.loading = false;
        },
        error: () => {
          this.error = 'No se pudo cargar el catálogo. Intenta nuevamente.';
          this.loading = false;
        },
      });
  }

  applySearch(): void {
    this.page = 1;
    this.loadCatalog();
  }

  resetFilters(): void {
    this.searchTerm = '';
    this.selectedCategory = '';
    this.selectedBranch = '';
    this.sortBy = '';
    this.page = 1;
    this.loadCatalog();
  }

  setPage(p: number): void {
    this.page = p;
    this.loadCatalog();
  }
}