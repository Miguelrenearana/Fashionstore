import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

@Component({
  selector: 'app-admin-ai-reports',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="ai">
      <h2>Reportes con IA (CU-32)</h2>
      <p class="hint">
        Escribe una consulta en lenguaje natural, por ejemplo: <em>"ventas por sucursal del último
        mes", "top 5 productos más vendidos", "stock agotado hoy"</em>.
      </p>

      @if (error) {
        <p class="error">{{ error }}</p>
      }

      <form class="prompt-form" (ngSubmit)="generate()">
        <textarea
          [(ngModel)]="prompt"
          name="prompt"
          rows="3"
          minlength="5"
          maxlength="2000"
          placeholder="Describe el reporte que necesitas…"
          required
        ></textarea>
        <div class="actions">
          <button type="submit" [disabled]="loading || prompt.trim().length < 5">
            {{ loading ? 'Generando…' : 'Generar reporte' }}
          </button>
          <button type="button" (click)="explain()" [disabled]="loading || prompt.trim().length < 5">
            Explicar SQL
          </button>
        </div>
      </form>

      @if (explanation()) {
        <section class="explain">
          <h3>Explicación</h3>
          <pre>{{ explanation() }}</pre>
        </section>
      }

      @if (result(); as res) {
        <section class="result">
          <h3>Resultado ({{ res.row_count }} filas · {{ res.execution_time_ms }} ms)</h3>
          @if (res.generated_sql) {
            <details>
              <summary>SQL generado</summary>
              <pre>{{ res.generated_sql }}</pre>
            </details>
          }
          <table>
            <thead>
              <tr>
                @for (col of res.columns; track col) {
                  <th>{{ col }}</th>
                }
              </tr>
            </thead>
            <tbody>
              @for (row of res.rows; track $index) {
                <tr>
                  @for (cell of row; track $index) {
                    <td>{{ cell }}</td>
                  }
                </tr>
              }
            </tbody>
          </table>
        </section>
      }
    </section>
  `,
  styles: [
    `
      .ai {
        max-width: 1000px;
      }
      .hint {
        color: #64748b;
        font-size: 0.9rem;
      }
      .error {
        color: #b00020;
      }
      .prompt-form textarea {
        width: 100%;
        box-sizing: border-box;
        font: inherit;
        padding: 0.6rem;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
      }
      .actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.6rem;
      }
      button {
        cursor: pointer;
        padding: 0.5rem 1rem;
      }
      button:disabled {
        opacity: 0.5;
      }
      .result,
      .explain {
        margin-top: 1.5rem;
      }
      pre {
        background: #0f172a;
        color: #e2e8f0;
        padding: 0.75rem;
        border-radius: 8px;
        overflow-x: auto;
        font-size: 0.8rem;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
      }
      th,
      td {
        border: 1px solid #ddd;
        padding: 0.35rem 0.5rem;
        text-align: left;
      }
      th {
        background: #f8fafc;
      }
      summary {
        cursor: pointer;
      }
    `,
  ],
})
export class AdminAiReportsComponent {
  private auth = inject(AuthService);

  readonly result = signal<any | null>(null);
  readonly explanation = signal<string | null>(null);

  prompt = '';
  loading = false;
  error = '';

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.auth.token()) h['Authorization'] = `Bearer ${this.auth.token()}`;
    return h;
  }

  generate(): void {
    this.loading = true;
    this.error = '';
    this.result.set(null);
    this.explanation.set(null);
    fetch(`${environment.apiUrl}/ai/reports/generate`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ prompt: this.prompt, max_rows: 100 }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const b = await r.json().catch(() => ({}));
          throw new Error(b.detail ?? r.statusText);
        }
        return r.json();
      })
      .then((res) => this.result.set(res))
      .catch((e) => (this.error = e.message ?? String(e)))
      .finally(() => (this.loading = false));
  }

  explain(): void {
    this.loading = true;
    this.error = '';
    this.explanation.set(null);
    fetch(`${environment.apiUrl}/ai/reports/explain?prompt=${encodeURIComponent(this.prompt)}`, {
      method: 'POST',
      headers: this.headers(),
    })
      .then(async (r) => {
        if (!r.ok) {
          const b = await r.json().catch(() => ({}));
          throw new Error(b.detail ?? r.statusText);
        }
        return r.json();
      })
      .then((res) =>
        this.explanation.set(`${res.sql ?? ''}\n\n${res.explanation ?? ''}`)
      )
      .catch((e) => (this.error = e.message ?? String(e)))
      .finally(() => (this.loading = false));
  }
}