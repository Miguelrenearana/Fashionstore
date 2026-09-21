import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [RouterLink],
  template: `
    <section class="hero">
      <h1>FashionStore</h1>
      <p class="lead">
        Plataforma inteligente de gestión de tienda de ropa: catálogo, inventario, reservas,
        punto de venta y reportes con IA para tu negocio.
      </p>
      <div class="cta">
        <a routerLink="/auth" class="btn btn-primary">Acceso restringido</a>
        <a href="fashionstore://fitting/1" class="btn btn-outline">Abrir probador virtual en la app</a>
      </div>
    </section>

    <section class="feature-grid">
      <article class="feature">
        <h2>Administración</h2>
        <p>Usuarios, roles y empleados con control de permisos.</p>
      </article>
      <article class="feature">
        <h2>Catálogo y productos</h2>
        <p>Tallas, colores, temporadas, colecciones y prendas de vestir.</p>
      </article>
      <article class="feature">
        <h2>Inventario por sucursal</h2>
        <p>Stock, reservas y ajustes en tiempo real.</p>
      </article>
      <article class="feature">
        <h2>POS y caja</h2>
        <p>Ventas presenciales, cobro y comprobantes.</p>
      </article>
      <article class="feature">
        <h2>Reservas de prendas</h2>
        <p>Preparación y atención de reservas del staff.</p>
      </article>
      <article class="feature">
        <h2>Reportes con IA</h2>
        <p>Consultas y reportes de ventas e inventario mediante IA.</p>
      </article>
    </section>
  `,
  styles: [
    `
      .hero {
        text-align: center;
        padding: 4rem 1.5rem 2rem;
        max-width: 720px;
        margin: 0 auto;
      }
      .hero h1 {
        font-size: clamp(2rem, 6vw, 3.5rem);
        margin: 0 0 1rem;
        color: var(--color-primary-dark, #cc7000);
      }
      .lead {
        font-size: clamp(1rem, 2.5vw, 1.25rem);
        color: var(--color-text-muted, #475569);
        margin: 0 0 1.5rem;
      }
      .cta {
        display: flex;
        justify-content: center;
        gap: 0.75rem;
        flex-wrap: wrap;
      }
      .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1rem;
        max-width: 960px;
        margin: 2rem auto 4rem;
        padding: 0 1.5rem;
      }
      .feature {
        border: 1px solid var(--color-border, #e2e8f0);
        border-radius: 12px;
        padding: 1.25rem;
        background: var(--color-surface, #fff);
      }
      .feature h2 {
        font-size: 1.1rem;
        margin: 0 0 0.5rem;
      }
      .feature p {
        margin: 0;
        color: var(--color-text-muted, #475569);
      }
    `,
  ],
})
export class LandingComponent {}