import { Component, inject, OnInit, ViewChild, ElementRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ClientService } from './client.service';

interface Msg {
  role: 'user' | 'assistant';
  content: string;
  typing?: boolean;
}

@Component({
  selector: 'app-client-chat',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="page chat-page">
      <h1 class="page-title">Asistente FashionStore</h1>
      <p class="page-subtitle">Inteligencia Artificial · Resuelve tus dudas sobre prendas, tallas y compras.</p>

      <div class="chat card" #chatBox>
        @for (m of messages; track $index) {
          <div class="bubble-row" [class.user]="m.role === 'user'">
            <div class="bubble" [class.user-bubble]="m.role === 'user'">
              @if (m.typing) {
                <span class="dots"><span></span><span></span><span></span></span>
              } @else {
                {{ m.content }}
              }
            </div>
          </div>
        }
      </div>

      <div class="input-bar">
        <input
          type="text"
          class="input"
          placeholder="Escribe tu consulta..."
          [(ngModel)]="input"
          (keyup.enter)="send()"
          [disabled]="sending"
        />
        <button type="button" class="btn btn-primary" (click)="send()" [disabled]="sending || !input.trim()">
          {{ sending ? '...' : '➤' }}
        </button>
      </div>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }
    </div>
  `,
  styles: [
    `
      .page-title { margin-bottom: 4px; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .chat-page { max-width: 760px; margin: 0 auto; display: flex; flex-direction: column; height: calc(100vh - 160px); }
      .chat { flex: 1; overflow-y: auto; padding: 1rem; margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
      .bubble-row { display: flex; }
      .bubble-row.user { justify-content: flex-end; }
      .bubble { max-width: 78%; background: var(--color-surface-variant, #f3f4f6); padding: 0.7rem 1rem; border-radius: 14px; border-top-left-radius: 4px; font-size: 0.92rem; white-space: pre-wrap; line-height: 1.45; }
      .user-bubble { background: var(--color-primary, #ff8c00); color: #fff; border-radius: 14px; border-top-right-radius: 4px; }
      .dots { display: inline-flex; gap: 4px; }
      .dots span { width: 7px; height: 7px; border-radius: 50%; background: var(--color-text-muted); animation: blink 1.2s infinite; }
      .dots span:nth-child(2) { animation-delay: 0.2s; }
      .dots span:nth-child(3) { animation-delay: 0.4s; }
      @keyframes blink { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
      .input-bar { display: flex; gap: 0.5rem; }
      .input-bar .input { flex: 1; }
    `,
  ],
})
export class ChatComponent implements OnInit {
  private api = inject(ClientService);
  @ViewChild('chatBox') chatBox?: ElementRef;

  messages: Msg[] = [];
  input = '';
  sending = false;
  error = '';

  ngOnInit(): void {
    this.messages = [{ role: 'assistant', content: '¡Hola! Soy la asistente de FashionStore. Pregúntame sobre prendas, tallas, disponibilidad o cómo hacer una reserva. 👋' }];
  }

  send(): void {
    const text = this.input.trim();
    if (!text || this.sending) return;
    this.input = '';
    this.error = '';
    this.messages.push({ role: 'user', content: text });

    const history: { role: 'user' | 'assistant'; content: string }[] = this.messages
      .filter((m) => !m.typing)
      .slice(0, 20)
      .map((m) => ({ role: m.role, content: m.content }));

    this.sending = true;
    this.messages.push({ role: 'assistant', content: '', typing: true });
    this.scroll();

    this.api.aiChat(text, history).subscribe({
      next: (res: any) => {
        const reply = res?.message ?? res?.reply ?? res?.response ?? 'No obtuve respuesta.';
        const len = this.messages.length;
        this.messages[len - 1] = { role: 'assistant', content: reply };
        this.sending = false;
        this.scroll();
      },
      error: () => {
        const len = this.messages.length;
        this.messages[len - 1] = { role: 'assistant', content: 'Lo siento, hubo un error al comunicarme con el servicio de IA. Intenta nuevamente.' };
        this.sending = false;
        this.scroll();
      },
    });
  }

  private scroll(): void {
    setTimeout(() => {
      this.chatBox?.nativeElement.scrollTo({ top: 999999, behavior: 'smooth' });
    }, 50);
  }
}