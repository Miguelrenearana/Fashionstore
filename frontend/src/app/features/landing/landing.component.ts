import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { UiButtonComponent } from '@shared/ui/button';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterLink, UiButtonComponent],
  template: `
    <section class="hero container py-12 md:py-20 text-center">
      <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-primary-dark mb-4">FashionStore</h1>
      <p class="lead text-lg text-text-muted mb-8 max-w-2xl mx-auto">
        Plataforma inteligente de gestión de tienda de ropa: catálogo, inventario, reservas,
        punto de venta y reportes con IA para tu negocio.
      </p>
      <div class="cta flex justify-center gap-4 flex-wrap">
        <ui-button variant="primary" size="lg" routerLink="/auth">
          Acceso restringido
        </ui-button>
        <ui-button variant="outline" size="lg" class="cursor-pointer" (click)="openFitting()">
          Abrir probador virtual en la app
        </ui-button>
      </div>
    </section>

    <section class="feature-grid container px-4 md:px-8 py-8 md:py-16">
      <article class="feature card p-6" *ngFor="let feature of features">
        <h2 class="text-xl font-semibold text-text mb-3">{{ feature.title }}</h2>
        <p class="text-text-muted">{{ feature.description }}</p>
      </article>
    </section>
  `,
  styles: []
})
export class LandingComponent {
  features = [
    { title: 'Administración', description: 'Usuarios, roles y empleados con control de permisos.' },
    { title: 'Catálogo y productos', description: 'Tallas, colores, temporadas, colecciones y prendas de vestir.' },
    { title: 'Inventario por sucursal', description: 'Stock, reservas y ajustes en tiempo real.' },
    { title: 'POS y caja', description: 'Ventas presenciales, cobro y comprobantes.' },
    { title: 'Reservas de prendas', description: 'Preparación y atención de reservas del staff.' },
    { title: 'Reportes con IA', description: 'Consultas y reportes de ventas e inventario mediante IA.' },
  ];

  openFitting() {
    window.location.href = 'fashionstore://fitting/1';
  }
}