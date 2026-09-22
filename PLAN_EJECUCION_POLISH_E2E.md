# Plan de Ejecución: Polish UI/UX + Testing E2E 34 CUs

> **Documento para que otra IA ejecute el plan completo**
> **Proyecto:** FashionStore (Web Angular + Mobile Flutter)
> **Scope:** 34 CUs E2E (CU-03 excluido - pendiente email real)
> **Tiempo estimado:** ~10h 15m
> **Autor:** Plan generado para ejecución autónoma

---

## 📋 Resumen del Scope

| Plataforma | Pantallas | CUs | Estado |
|------------|-----------|-----|--------|
| **Web** | 14 existentes | 20 CUs | Admin/Staff/POS/Landing/Auth |
| **Móvil** | 18 existentes + 1 nueva | 14 CUs | Customer completo + CU-11 |
| **Total** | 33 pantallas | **34 CUs** | CU-03 fuera de scope |

---

## 🎯 FASE 0: Tokens Unificados (45 min)

### Objetivo
Crear `design-tokens.json` como *single source of truth* que genere:
- CSS variables → `frontend/src/styles/design-system.css`
- Dart tokens → `mobile/lib/core/design/design_tokens.dart`

### Archivo: `design-tokens.json` (raíz del proyecto)

```json
{
  "color": {
    "primary": "#FF8C00",
    "primaryHover": "#E67E00",
    "primaryLight": "#FFF3E0",
    "primaryDark": "#CC7000",
    "primaryContrast": "#FFFFFF",
    "nav": "#1A2B3A",
    "navHover": "#243B4E",
    "surface": "#FFFFFF",
    "surfaceAlt": "#F8FAFC",
    "bg": "#F5F7FA",
    "text": "#1E293B",
    "textSecondary": "#64748B",
    "textMuted": "#94A3B8",
    "textOnPrimary": "#FFFFFF",
    "border": "#E2E8F0",
    "borderFocus": "#FF8C00",
    "success": "#059669",
    "successLight": "#ECFDF5",
    "warning": "#D97706",
    "warningLight": "#FFFBEB",
    "error": "#DC2626",
    "errorLight": "#FEF2F2",
    "info": "#0284C7",
    "infoLight": "#E0F2FE"
  },
  "spacing": {
    "1": "4px", "2": "8px", "3": "12px", "4": "16px",
    "5": "24px", "6": "32px", "8": "48px"
  },
  "radius": {
    "sm": "4px", "md": "8px", "lg": "12px", "full": "9999px"
  },
  "shadow": {
    "sm": "0 1px 2px rgba(15,23,42,0.05)",
    "md": "0 4px 6px rgba(15,23,42,0.07)",
    "lg": "0 10px 15px rgba(15,23,42,0.1)",
    "focus": "0 0 0 3px rgba(255,140,0,0.25)"
  },
  "typography": {
    "fontFamily": "Inter",
    "displayFamily": "Geist",
    "xs": "12px", "sm": "14px", "base": "16px",
    "lg": "18px", "xl": "20px", "2xl": "24px", "3xl": "30px"
  },
  "zIndex": {
    "dropdown": 100, "sticky": 200, "modal": 300, "toast": 400
  },
  "breakpoints": {
    "sm": "640px", "md": "768px", "lg": "1024px", "xl": "1280px", "xxl": "1536px"
  }
}
```

### Scripts de Generación

#### 1. `scripts/generate-tokens.js` (Node.js)

```js
const fs = require('fs');
const path = require('path');

const tokens = JSON.parse(fs.readFileSync('design-tokens.json', 'utf8'));

// Generar CSS variables
let css = ':root {\n';
function flatten(obj, prefix = '') {
  Object.entries(obj).forEach(([key, value]) => {
    const newKey = prefix ? `${prefix}-${key}` : key;
    if (typeof value === 'object' && value !== null) {
      flatten(value, newKey);
    } else {
      css += `  --${newKey.replace(/([A-Z])/g, '-$1').toLowerCase()}: ${value};\n`;
    }
  });
}
flatten(tokens.color);
flatten(tokens.spacing);
flatten(tokens.radius);
flatten(tokens.shadow);
flatten(tokens.typography);
flatten(tokens.zIndex);
css += '}\n';

// Dark mode
css += '\n@media (prefers-color-scheme: dark) {\n  :root {\n';
const darkOverrides = {
  'color-nav': '#0F172A',
  'color-nav-hover': '#1E293B',
  'color-surface': '#1E293B',
  'color-surface-alt': '#0F172A',
  'color-bg': '#0A0F1A',
  'color-text': '#F1F5F9',
  'color-text-secondary': '#94A3B8',
  'color-text-muted': '#64748B',
  'color-border': '#334155',
  'color-primary-light': '#7C3A00',
  'shadow-sm': '0 1px 2px rgba(0,0,0,0.3)',
  'shadow-md': '0 4px 6px rgba(0,0,0,0.4)',
  'shadow-lg': '0 10px 15px rgba(0,0,0,0.5)'
};
Object.entries(darkOverrides).forEach(([k, v]) => {
  css += `    --${k}: ${v};\n`;
});
css += '  }\n}\n';

fs.writeFileSync('frontend/src/styles/design-system.css', css);
console.log('✅ CSS generado: frontend/src/styles/design-system.css');
```

#### 2. `mobile/tools/generate_tokens.dart` (Dart)

```dart
import 'dart:io';
import 'dart:convert';

void main() async {
  final tokensFile = File('design-tokens.json');
  final tokens = jsonDecode(await tokensFile.readAsString()) as Map<String, dynamic>;

  final buffer = StringBuffer();
  buffer.writeln('// GENERADO AUTOMÁTICAMENTE - NO EDITAR MANUALMENTE');
  buffer.writeln('// Ejecutar: dart run tools/generate_tokens.dart');
  buffer.writeln('');
  buffer.writeln('import \'package:flutter/widgets.dart\';');
  buffer.writeln('');

  // Colores
  buffer.writeln('class AppColors {');
  final colors = tokens['color'] as Map<String, dynamic>;
  colors.forEach((key, value) {
    final hex = (value as String).replaceFirst('#', '0xFF');
    buffer.writeln('  static const ${_toCamelCase(key)} = Color($hex);');
  });
  buffer.writeln('}');

  // Espaciado
  buffer.writeln('class AppSpacing {');
  final spacing = tokens['spacing'] as Map<String, dynamic>;
  spacing.forEach((key, value) {
    final px = double.parse(value.replaceAll('px', ''));
    buffer.writeln('  static const double x${key} = ${px.toStringAsFixed(1)};');
  });
  buffer.writeln('}');

  // Radius
  buffer.writeln('class AppRadius {');
  final radius = tokens['radius'] as Map<String, dynamic>;
  radius.forEach((key, value) {
    final px = double.parse(value.replaceAll('px', ''));
    buffer.writeln('  static const double ${key} = ${px.toStringAsFixed(1)};');
  });
  buffer.writeln('}');

  // Shadows
  buffer.writeln('class AppShadows {');
  final shadows = tokens['shadow'] as Map<String, dynamic>;
  shadows.forEach((key, value) {
    buffer.writeln('  static const List<BoxShadow> ${key} = [');
    buffer.writeln('    BoxShadow(');
    buffer.writeln('      color: ${_parseShadowColor(value)},');
    buffer.writeln('      offset: Offset(0, ${_parseShadowOffset(value)}),');
    buffer.writeln('      blurRadius: ${_parseShadowBlur(value)},');
    buffer.writeln('      spreadRadius: ${_parseShadowSpread(value)},');
    buffer.writeln('    ),');
    buffer.writeln('  ];');
  });
  buffer.writeln('}');

  // Typography
  buffer.writeln('class AppTypography {');
  buffer.writeln('  static const String fontFamily = \'${tokens['typography']['fontFamily']}\';');
  buffer.writeln('  static const String displayFamily = \'${tokens['typography']['displayFamily']}\';');
  final typo = tokens['typography'] as Map<String, dynamic>;
  typo.forEach((key, value) {
    if (key != 'fontFamily' && key != 'displayFamily') {
      final px = double.parse(value.replaceAll('px', ''));
      buffer.writeln('  static const TextStyle ${key} = TextStyle(');
      buffer.writeln('    fontSize: ${px.toStringAsFixed(1)},');
      buffer.writeln('    fontWeight: FontWeight.w400,');
      buffer.writeln('    height: 1.5,');
      buffer.writeln('  );');
    }
  });
  buffer.writeln('}');

  // Z-Index
  buffer.writeln('class AppZIndex {');
  final zIndex = tokens['zIndex'] as Map<String, dynamic>;
  zIndex.forEach((key, value) {
    buffer.writeln('  static const int ${key} = $value;');
  });
  buffer.writeln('}');

  final outputFile = File('mobile/lib/core/design/design_tokens.dart');
  await outputFile.writeAsString(buffer.toString());
  print('✅ Dart tokens generado: mobile/lib/core/design/design_tokens.dart');
}

String _toCamelCase(String s) => s.replaceAllMapped(RegExp(r'-([a-z])'), (m) => m[1]!.toUpperCase());

String _parseShadowColor(String shadow) {
  final match = RegExp(r'rgba?\(([^)]+)\)').firstMatch(shadow);
  if (match != null) {
    final parts = match[1]!.split(',').map((e) => e.trim()).toList();
    if (parts.length == 4) {
      return 'Color.fromRGBO(${parts[0]}, ${parts[1]}, ${parts[2]}, ${parts[3]})';
    }
    return 'Color.fromRGBO(${parts[0]}, ${parts[1]}, ${parts[2]}, 1)';
  }
  return 'Colors.black';
}

int _parseShadowOffset(String shadow) {
  final match = RegExp(r'offset:\s*(\d+)').firstMatch(shadow);
  return match != null ? int.parse(match[1]!) : 4;
}

int _parseShadowBlur(String shadow) {
  final match = RegExp(r'blurRadius:\s*(\d+)').firstMatch(shadow);
  return match != null ? int.parse(match[1]!) : 6;
}

int _parseShadowSpread(String shadow) {
  final match = RegExp(r'spreadRadius:\s*(-?\d+)').firstMatch(shadow);
  return match != null ? int.parse(match[1]!) : 0;
}
```

### Comandos de Ejecución

```bash
# En raíz del proyecto
node scripts/generate-tokens.js
cd mobile && dart run tools/generate_tokens.dart
```

### Verificación
- `frontend/src/styles/design-system.css` actualizado
- `mobile/lib/core/design/design_tokens.dart` actualizado
- No hay valores hardcoded en componentes

---

## 🎯 FASE 1: Web Component Library (1.5h)

### Objetivo
Crear 12 componentes standalone en `frontend/src/app/shared/ui/` usando signals y las utilities CSS existentes.

### Estructura por Componente

```
shared/ui/
├── button/
│   ├── button.component.ts
│   ├── button.component.html (opcional, inline template)
│   └── index.ts
├── input/
├── card/
├── modal/
├── select/
├── table/
├── tabs/
├── badge/
├── chip/
├── avatar/
├── toast/
└── skeleton/
```

### 1.1 UiButtonComponent - button.component.ts

```ts
import { Component, input, output, HostBinding, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
export type ButtonSize = 'sm' | 'md' | 'lg' | 'icon';

@Component({
  selector: 'ui-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [type]="type()"
      [disabled]="disabled() || loading()"
      [class]="computedClasses()"
      (click)="onClick($event)">
      @if (loading()) {
        <span class="spinner" aria-hidden="true"></span>
      } @else if (icon() && !label()) {
        <span class="icon">{{ icon() }}</span>
      } @else {
        @if (icon()) { <span class="icon">{{ icon() }}</span> }
        @if (label()) { <span class="label">{{ label() }}</span> }
      }
    </button>
  `,
  styles: [`
    :host { display: inline-flex; }
    button {
      display: inline-flex; align-items: center; justify-content: center;
      gap: var(--space-2); border: 1px solid transparent; border-radius: var(--radius-md);
      font-family: var(--font-sans); font-weight: 500; cursor: pointer;
      transition: all var(--transition-fast); text-decoration: none; white-space: nowrap;
    }
    button:disabled { opacity: 0.5; cursor: not-allowed; pointer-events: none; }
    .spinner { width: 16px; height: 16px; border: 2px solid currentColor; border-right-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .icon { font-size: 1.2em; line-height: 1; }
  `]
})
export class UiButtonComponent {
  // Inputs
  label = input<string>('');
  icon = input<string>('');
  variant = input<ButtonVariant>('primary');
  size = input<ButtonSize>('md');
  type = input<'button' | 'submit' | 'reset'>('button');
  disabled = input(false);
  loading = input(false);
  ariaLabel = input<string>('');

  // Output
  clicked = output<MouseEvent>();

  // Computed classes
  computedClasses = computed(() => {
    const base = 'btn';
    const v = `btn-${this.variant()}`;
    const s = this.size() !== 'md' ? `btn-${this.size()}` : '';
    const loading = this.loading() ? 'btn-loading' : '';
    return [base, v, s, loading].filter(Boolean).join(' ');
  });

  onClick(event: MouseEvent) {
    if (!this.disabled() && !this.loading()) {
      this.clicked.emit(event);
    }
  }
}
```

### 1.2 UiInputComponent - input.component.ts

```ts
import { Component, input, output, forwardRef, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormsModule } from '@angular/forms';

export type InputType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';

@Component({
  selector: 'ui-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => UiInputComponent),
    multi: true
  }],
  template: `
    <div class="form-field">
      @if (label()) {
        <label class="form-label" [for]="id()">{{ label() }}</label>
      }
      <div class="input-wrapper">
        @if (prefixIcon()) {
          <span class="prefix-icon">{{ prefixIcon() }}</span>
        }
        <input
          [id]="id()"
          [type]="type()"
          [placeholder]="placeholder()"
          [disabled]="disabled()"
          [readonly]="readonly()"
          [class]="computedClasses()"
          [value]="value()"
          (input)="onInput($event)"
          (blur)="onBlur()"
          (focus)="onFocus()"
          [attr.aria-label]="ariaLabel()"
          [attr.aria-describedby]="describedBy()"
          [attr.aria-invalid]="error() ? 'true' : 'false'"
        />
        @if (suffixIcon()) {
          <span class="suffix-icon">{{ suffixIcon() }}</span>
        }
      </div>
      @if (hint() && !error()) {
        <span class="form-hint">{{ hint() }}</span>
      }
      @if (error()) {
        <span class="form-error">{{ error() }}</span>
      }
    </div>
  `,
  styles: [`
    .input-wrapper { position: relative; display: flex; align-items: center; }
    .prefix-icon, .suffix-icon { position: absolute; color: var(--color-text-muted); pointer-events: none; }
    .prefix-icon { left: var(--space-3); }
    .suffix-icon { right: var(--space-3); }
    input { width: 100%; padding: var(--space-2) var(--space-3); font-size: var(--text-base); }
    input:focus { outline: none; border-color: var(--color-border-focus); box-shadow: var(--shadow-focus); }
    input[readonly] { background: var(--color-surface-alt); }
    .form-field { display: flex; flex-direction: column; gap: var(--space-1); }
    .form-label { font-size: var(--text-sm); font-weight: 500; color: var(--color-text); }
    .form-hint { font-size: var(--text-xs); color: var(--color-text-muted); }
    .form-error { font-size: var(--text-xs); color: var(--color-error); }
  `]
})
export class UiInputComponent implements ControlValueAccessor {
  // Inputs
  label = input<string>('');
  placeholder = input<string>('');
  type = input<InputType>('text');
  prefixIcon = input<string>('');
  suffixIcon = input<string>('');
  disabled = input(false);
  readonly = input(false);
  error = input<string>('');
  hint = input<string>('');
  ariaLabel = input<string>('');
  id = input<string>(`ui-input-${Math.random().toString(36).slice(2)}`);
  describedBy = input<string>('');

  // Internal
  value = signal('');
  focused = signal(false);
  private onChange = (v: string) => {};
  private onTouched = () => {};

  computedClasses = computed(() => {
    const base = 'form-input';
    const err = this.error() ? 'error' : '';
    const focus = this.focused() ? 'focus' : '';
    return [base, err, focus].filter(Boolean).join(' ');
  });

  onInput(event: Event) {
    const val = (event.target as HTMLInputElement).value;
    this.value.set(val);
    this.onChange(val);
  }

  onBlur() { this.focused.set(false); this.onTouched(); }
  onFocus() { this.focused.set(true); }

  writeValue(val: string): void { this.value.set(val ?? ''); }
  registerOnChange(fn: (v: string) => void): void { this.onChange = fn; }
  registerOnTouched(fn: () => void): void { this.onTouched = fn; }
  setDisabledState(disabled: boolean): void { this.disabled.set(disabled); }
}
```

### 1.3 Resto de Componentes (Patrón Similar)

| Componente | Archivo | Clases CSS Base |
|------------|---------|-----------------|
| UiCard | card.component.ts | `.card`, `.card-header`, `.card-body`, `.card-footer` |
| UiModal | modal.component.ts | `.modal-overlay`, `.modal`, `.modal-header`, `.modal-body`, `.modal-footer` |
| UiSelect | select.component.ts | `.form-select` + options |
| UiTable | table.component.ts | `.table-wrapper`, `.table`, responsive |
| UiTabs | tabs.component.ts | `.tabs`, `.tab`, `.tab-panel` |
| UiBadge | badge.component.ts | `.badge`, `.badge-*` |
| UiChip | chip.component.ts | `.chip`, `.chip-removable` |
| UiAvatar | avatar.component.ts | `.avatar`, `.avatar-*` |
| UiToast | toast.service.ts + toast.component.ts | `.alert`, `.alert-*` |
| UiSkeleton | skeleton.component.ts | `.skeleton`, `.skeleton-*` |

### Barrel Export: `shared/ui/index.ts`

```ts
export * from './button/button.component';
export * from './input/input.component';
export * from './card/card.component';
export * from './modal/modal.component';
export * from './select/select.component';
export * from './table/table.component';
export * from './tabs/tabs.component';
export * from './badge/badge.component';
export * from './chip/chip.component';
export * from './avatar/avatar.component';
export * from './toast/toast.service';
export * from './toast/toast.component';
export * from './skeleton/skeleton.component';
```

### Verificación Fase 1

```bash
cd frontend
npm run build  # Debe compilar sin errores
# Verificar en Storybook (si existe) o crear demo page temporal
```

---

## 🎯 FASE 2: Web Polish - 14 Pantallas (2h)

### Pantallas a Actualizar (Orden de Prioridad)

| # | Pantalla | Archivo | CUs |
|---|----------|---------|-----|
| 1 | Landing | features/landing/landing.component.ts | — |
| 2 | Login | features/auth/login.component.ts | CU-01 |
| 3 | Forgot Password | features/auth/forgot-password.component.ts | CU-03* |
| 4 | Reset Password | features/auth/reset-password.component.ts | CU-03* |
| 5 | AdminUsers | features/admin/admin-users.component.ts | CU-04 |
| 6 | AdminProducts | features/admin/admin-products.component.ts | CU-07 |
| 7 | AdminCatalogConfig | features/admin/admin-catalog-config.component.ts | CU-06,08,09,10 |
| 8 | AdminInventory | features/admin/admin-inventory.component.ts | CU-27,28,29 |
| 9 | AdminPromotions | features/admin/admin-promotions.component.ts | CU-11 |
| 10 | AdminReports | features/admin/admin-reports.component.ts | CU-33,34,35 |
| 11 | AdminAIReports | features/admin/admin-ai-reports.component.ts | CU-32 |
| 12 | StaffReservations | features/staff/staff-reservations.component.ts | CU-17,18 |
| 13 | POS | features/pos/pos.component.ts | CU-23,24 |
| 14 | AdminShell | features/admin/admin-shell.component.ts | Nav |

*\*CU-03: Solo UI visual, funcionalidad mock se mantiene*

### Patrones de Migración Comunes

**Antes (CSS inline)**

```ts
styles: [`
  .login { max-width: 360px; margin: 3rem auto; gap: 0.75rem; }
  input, button { padding: 0.625rem; border-radius: 6px; border: 1px solid #ccc; }
  button { background: var(--color-primary); color: #fff; border: none; }
`]
```

**Después (Componentes + Utilities)**

```html
<ui-card class="w-full max-w-md mx-auto mt-20 p-6">
  <h2 class="text-2xl font-semibold mb-6 text-center">Iniciar sesión</h2>
  <form (ngSubmit)="onSubmit()" class="flex flex-col gap-4">
    <ui-input
      label="Email"
      type="email"
      placeholder="usuario@fashionstore.dev"
      [(ngModel)]="email"
      [error]="emailError()"
      required>
    </ui-input>
    <ui-input
      label="Contraseña"
      type="password"
      placeholder="••••••••"
      [(ngModel)]="password"
      [error]="passwordError()"
      required>
    </ui-input>
    <ui-button variant="primary" size="lg" class="w-full" [loading]="loading()">
      Entrar
    </ui-button>
  </form>
  <p class="text-center text-sm text-secondary">
    <a routerLink="/auth/forgot-password" class="text-primary hover:underline">¿Olvidé mi contraseña?</a>
  </p>
</ui-card>
```

### Checklist por Pantalla
- Imports de `shared/ui` components
- Reemplazo de HTML inline por componentes
- Uso de utilities CSS (`gap-4`, `p-4`, `text-primary`, etc.)
- Estados de carga: `UiSkeleton` en listas, `loading()` en botones
- Estados vacíos: `UiEmptyState` donde aplique
- Toasts: `ToastService` para feedback
- Responsive: utilities `grid-cols-*`, `flex-col`, `md:flex-row`
- Dark mode: verificar variables CSS funcionan

### Verificación Fase 2

```bash
cd frontend
npm run build
npm run lint  # Si existe
# Test manual rápido: Login → Admin → POS
```

---

## 🎯 FASE 3: Mobile Polish + CU-11 (4h)

### 3.1 Theme & Animations Base (45 min)

`mobile/lib/core/animation/app_animations.dart`

```dart
import 'package:flutter/widgets.dart';

class AppAnimations {
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration base = Duration(milliseconds: 200);
  static const Duration slow = Duration(milliseconds: 300);

  static Curve get easeOut => Curves.easeOutCubic;
  static Curve get easeIn => Curves.easeInCubic;
  static Curve get easeInOut => Curves.easeInOutCubic;

  // Fade
  static Widget fadeIn({required Widget child, Duration duration = base}) {
    return AnimatedOpacity(
      opacity: 1.0,
      duration: duration,
      curve: easeOut,
      child: child,
    );
  }

  // Slide Up
  static Widget slideUp({required Widget child, Duration duration = base, double offset = 20}) {
    return TweenAnimationBuilder<Offset>(
      tween: Tween(begin: Offset(0, offset), end: Offset.zero),
      duration: duration,
      curve: easeOut,
      builder: (context, value, child) => Transform.translate(offset: value * MediaQuery.sizeOf(context).height, child: child),
      child: child,
    );
  }

  // Scale Tap
  static Widget scaleTap({required Widget child, required VoidCallback onTap}) {
    return GestureDetector(
      onTapDown: (_) => {},
      onTapUp: (_) => onTap(),
      onTapCancel: () => {},
      child: AnimatedScale(
        scale: 1.0,
        duration: Duration(milliseconds: 100),
        curve: Curves.easeOut,
        child: child,
      ),
    );
  }

  // Shimmer
  static Widget shimmer({required Widget child}) {
    return ShaderMask(
      shaderCallback: (bounds) => LinearGradient(
        colors: [Colors.grey[300]!, Colors.grey[100]!, Colors.grey[300]!],
        stops: [0.1, 0.5, 0.9],
        transform: GradientRotation(0.5),
      ).createShader(bounds),
      blendMode: BlendMode.srcATop,
      child: child,
    );
  }

  // Stagger List
  static List<Widget> stagger(List<Widget> children, {Duration delay = const Duration(milliseconds: 100)}) {
    return children.asMap().entries.map((entry) {
      final index = entry.key;
      final child = entry.value;
      return TweenAnimationBuilder<double>(
        tween: Tween(begin: 0.0, end: 1.0),
        duration: Duration(milliseconds: 300 + index * delay.inMilliseconds),
        curve: Curves.easeOut,
        builder: (context, value, child) => Opacity(
          opacity: value,
          child: Transform.translate(offset: Offset(0, 20 * (1 - value)), child: child),
        ),
        child: child,
      );
    }).toList();
  }
}
```

**Actualizar AppTheme - Agregar Page Transitions**

```dart
// En app_theme.dart, dentro de _build():
pageTransitionsTheme: PageTransitionsTheme(builders: {
  TargetPlatform.android: CupertinoPageTransitionsBuilder(),
  TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
  TargetPlatform.windows: CupertinoPageTransitionsBuilder(),
  TargetPlatform.macOS: CupertinoPageTransitionsBuilder(),
  TargetPlatform.linux: CupertinoPageTransitionsBuilder(),
}),
```

### 3.2 Empty States SVGs (30 min)

Crear 6 SVGs en `mobile/assets/images/empty/`:
- `empty_cart.svg` - Carrito vacío
- `empty_history.svg` - Historial vacío
- `empty_search.svg` - Sin resultados
- `empty_notifications.svg` - Sin notificaciones
- `error_generic.svg` - Error genérico
- `success_check.svg` - Éxito

Ejemplo `empty_cart.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="80" fill="#FFF3E0"/>
  <path d="M60 100 L85 125 L140 70" stroke="#FF8C00" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="60" cy="100" r="8" fill="#FF8C00"/>
  <circle cx="140" cy="70" r="8" fill="#FF8C00"/>
</svg>
```

### 3.3 Nueva Pantalla: PromotionsScreen (CU-11) - 45 min

Archivo: `mobile/lib/features/promotions/promotions_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/design/design.dart';
import '../../shared/widgets/shared_widgets.dart';

class PromotionsScreen extends ConsumerWidget {
  const PromotionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final promotionsAsync = ref.watch(promotionsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Promociones')),
      body: promotionsAsync.when(
        data: (promotions) {
          if (promotions.isEmpty) {
            return AppEmptyState(
              icon: 'assets/images/empty/empty_notifications.svg',
              title: 'Sin promociones',
              message: 'No hay promociones activas en este momento.',
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(AppSpacing.x4),
            itemCount: promotions.length,
            itemBuilder: (context, index) {
              final promo = promotions[index];
              return _PromoCard(promo: promo);
            },
          );
        },
        loading: () => ListView.builder(
          padding: const EdgeInsets.all(AppSpacing.x4),
          itemCount: 6,
          itemBuilder: (_, __) => AppSkeleton.card(),
        ),
        error: (e, _) => AppEmptyState(
          icon: 'assets/images/empty/error_generic.svg',
          title: 'Error al cargar',
          message: e.toString(),
          actionLabel: 'Reintentar',
          onAction: () => ref.invalidate(promotionsProvider),
        ),
      ),
    );
  }
}

class _PromoCard extends StatelessWidget {
  final Promotion promo;
  const _PromoCard({required this.promo});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      onTap: () => _showDetail(context),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              AppBadge(
                label: '${promo.discountPercent}% OFF',
                variant: BadgeVariant.primary,
              ),
              const Spacer(),
              Text(
                _formatDate(promo.endAt),
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.x3),
          Text(promo.name, style: Theme.of(context).textTheme.titleMedium),
          if (promo.description != null) ...[
            const SizedBox(height: AppSpacing.x2),
            Text(promo.description!, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary)),
          ],
        ],
      ),
    );
  }

  void _showDetail(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        minChildSize: 0.4,
        expand: false,
        builder: (_, controller) => SingleChildScrollView(
          controller: controller,
          padding: const EdgeInsets.all(AppSpacing.x5),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(promo.name, style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: AppSpacing.x2),
              Text('${promo.discountPercent}% de descuento', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: AppColors.primary)),
              const SizedBox(height: AppSpacing.x3),
              Text('Válida del ${_formatDate(promo.startAt)} al ${_formatDate(promo.endAt)}'),
              const SizedBox(height: AppSpacing.x3),
              Text('Productos incluidos:', style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: AppSpacing.x2),
              Wrap(
                spacing: AppSpacing.x2,
                runSpacing: AppSpacing.x2,
                children: promo.garments.map((g) => AppChip(label: g.name)).toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime dt) => '${dt.day}/${dt.month}/${dt.year}';
}
```

**Agregar ruta en `catalog_routes.dart`:**

```dart
GoRoute(
  path: 'promotions',
  name: 'promotions',
  builder: (context, state) => const PromotionsScreen(),
),
```

### 3.4 Polish Pantallas Existentes (2h 15 min)

| Pantalla | Archivo | Polish Clave |
|----------|---------|--------------|
| Auth (4) | login_screen.dart, register_screen.dart, forgot_password_screen.dart, reset_password_screen.dart | Biometric (login), ilustraciones empty state, hero transitions entre pantallas, AppTextField + AppButton consistentes |
| CatalogScreen | catalog_screen.dart | SliverAppBar con search, chips categorías sticky horizontal, grid AppCard con hero images, pull-to-refresh, skeleton grid |
| ProductDetailScreen | product_detail_screen.dart | Hero image parallax, bottom sheet variantes (tallas/colores), stock por sucursal con AppBadge, CTA AR fitting prominente |
| ReservationsList | reservations_screen.dart | Timeline visual con AppStepper, swipe actions (cancelar), empty state ilustración |
| ReservationDetail | reservation_detail_screen.dart | Detalle completo, código QR retiro, actions según estado |
| CartScreen | cart_screen.dart | Swipe delete (Dismissible), stepper cantidad, promo code AppTextField, sticky checkout bar AppButton block |
| CheckoutScreen | checkout_screen.dart | Single-page: dirección → pago → confirmar, QR payment integrado, Apple/Google Pay buttons |
| AIChatScreen | ai_chat_screen.dart | Streaming bubbles (typewriter), suggested chips, copy/regenerate actions |
| RecommendationsScreen | recommendations_screen.dart | Grid cards + skeletons, filter chips (similares/historial/trending) |
| ProfileScreen | profile_screen.dart | Avatar upload (camera/gallery), settings grouped AppCard, logout confirmation modal |
| NotificationsScreen | notifications_screen.dart | Mostrar token reset prominentemente (CU-03 UX), list con AppBadge unread, swipe mark read |
| PurchaseHistoryScreen | purchase_history_screen.dart | Timeline orders con AppStepper status, detail modal con receipt |
| ARFittingScreen | ar_fitting_screen.dart | Assets reales, anclaje automático, selector prendas chips, deep link test |
| MainShell/BottomNav | app_shell.dart, app_bottom_nav.dart | Badges en tabs, FAB AR, page transitions suaves |

### 3.5 Deep Links Test (15 min)

Verificar en `android/app/src/main/AndroidManifest.xml`:

```xml
<activity android:name=".MainActivity" ...>
  <intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="fashionstore" android:host="fitting" />
  </intent-filter>
</activity>
```

Test manual:

```bash
adb shell am start -W -a android.intent.action.VIEW -d "fashionstore://fitting/123" com.fashionstore.app
```

### Verificación Fase 3

```bash
cd mobile
flutter analyze
flutter test
flutter build apk --release --split-per-abi
# Test en device físico: flutter install
```

---

## 🎯 FASE 4: Verificación E2E 34 CUs (1.5h)

### 4.1 Checklist Web Admin (Chrome PC)

| CU | Acción | Verificación |
|----|--------|--------------|
| CU-01 | Login web | JWT guardado, redirect según rol |
| CU-02 | Logout | Limpia sesión, redirect landing |
| CU-04 | AdminUsers | CRUD usuarios, asignar roles, validaciones |
| CU-06 | AdminCatalogConfig > Ciudades/Sucursales | CRUD completo, validaciones |
| CU-07 | AdminProducts | CRUD productos, soft delete, imagen upload, 11 tests pasan |
| CU-08 | AdminCatalogConfig > Categorías | CRUD + jerarquía |
| CU-09 | AdminCatalogConfig > Temporadas/Colecciones | CRUD + fechas |
| CU-10 | AdminCatalogConfig > Proveedores | CRUD + asociación productos |
| CU-11 | AdminPromotions | CRUD promociones, fechas, asociación prendas |
| CU-17 | StaffReservations | Lista reservas, filtros, preparación |
| CU-18 | StaffReservations | Preparación prendas reservadas |
| CU-23 | POS | Venta completa, carrito, pago caja |
| CU-24 | POS | Comprobante generado, impresión |
| CU-27 | AdminInventory | Existencias por sucursal, ajustes |
| CU-28 | AdminInventory | Movimientos (filtros, tipos) |
| CU-29 | AdminInventory | Recepción productos (crear + recibir) |
| CU-32 | AdminAIReports | NL→SQL consulta, resultados |
| CU-33 | AdminReports | KPIs ventas, stock, rotación, top productos |
| CU-34 | AdminReports | AuditLog filtros (usuario, acción, entidad, fechas) |
| CU-35 | AdminReports | Consolidado por sucursal, export Excel |

### 4.2 Checklist Mobile Customer (Device Físico Android)

| CU | Pantalla | Acción | Verificación |
|----|----------|--------|--------------|
| CU-01 | Login | Login + biometric | JWT, redirect catálogo |
| CU-05 | Register/Profile | Registro + edición perfil | Datos guardados, avatar upload |
| CU-11 | PromotionsScreen | Lista promos activas | Chips filtro, detalle bottom sheet |
| CU-12 | CatalogScreen | Navegación, búsqueda, filtros | Grid, chips categorías, pull-refresh |
| CU-13 | ProductDetail | Buscar/filtrar prendas | Filtros funcionan |
| CU-14 | ProductDetail | Disponibilidad sucursal | Stock por sucursal visible |
| CU-15 | Reservations | Crear reserva múltiples prendas | Seleccionar prendas, sucursal, confirmar |
| CU-16 | Reservations | Cancelar reserva | Swipe cancelar, confirmación |
| CU-18 | Reservations | Preparación (staff view) | Estados actualizan |
| CU-19 | ARFitting | Probar en device físico | Assets reales, anclaje automático, selector prendas |
| CU-20 | CartScreen | Add/remove/update qty + promo | Totales correctos, sticky bar |
| CU-21 | CheckoutScreen | Compra single-page | Dirección, pago QR, confirmación |
| CU-22 | PurchaseHistory | Timeline órdenes | Detalle + receipt modal |
| CU-25 | CheckoutScreen | QR payment mock | QR SVG, auto-complete, webhook |
| CU-26 | PurchaseHistory | Ver comprobantes | Detalle items, RNC/CUF |
| CU-30 | RecommendationsScreen | Grid recomendaciones | 3 fuentes: similar/historial/trending |
| CU-31 | AIChatScreen | Chat streaming | Burbujas typewriter, chips sugeridos |

### 4.3 Checklist Cross-Device

| Test | Acción | Verificación |
|------|--------|--------------|
| Deep Link AR | adb shell am start -d "fashionstore://fitting/123" | Abre ARFittingScreen con variante 123 |
| Web→Mobile Notif | Web: Forgot Password → email real | Móvil: NotificationsScreen muestra token |
| AR Assets | ARFittingScreen | Prendas PNG transparentes, anclaje hombros-caderas |

### 4.4 Comandos de Verificación Automatizada

```bash
# Backend tests
cd backend && .venv/Scripts/python.exe -m pytest tests/ -q --tb=no

# Frontend build + lint
cd frontend && npm run build && npm run lint

# Mobile analyze + test + build
cd mobile && flutter analyze && flutter test && flutter build apk --release --split-per-abi
```

---

## 🎯 FASE 5: Build & Deploy Verification (30 min)

### 5.1 Web Deploy Check

```bash
cd frontend
npm run build
# Verificar dist/ generado
# Verificar vercel.json rewrites
# Deploy manual a Vercel o verificar CI/CD
```

### 5.2 Mobile APK Check

```bash
cd mobile
flutter build apk --release --split-per-abi
# Verificar: build/app/outputs/flutter-apk/app-release.apk
# Tamaño < 100MB
# Instalar en device: flutter install
```

### 5.3 Backend Health Check

```bash
curl https://tu-backend.render.com/health
# Debe responder 200 OK con {status: "healthy"}
```

---

## ✅ Definition of Done (Global)

- **Tokens**: design-tokens.json genera CSS + Dart sin errores
- **Web Components**: 12 componentes compilan, Storybook/demo funciona
- **Web Polish**: 14 pantallas migradas, responsive, dark mode OK
- **Mobile Polish**: 18 pantallas + 1 nueva (CU-11), animaciones fluidas, empty states
- **E2E 34 CUs**: Checklists web + mobile + cross-device pasan
- **Builds**: Web + Mobile + Backend health check OK
- **APK**: Generado, instalable, testeado en device físico
- **Documentación**: TODO.md actualizado, CHANGES.md si existe

---

## 🚨 Troubleshooting Común

| Error | Solución |
|-------|----------|
| design-tokens.json parse error | Validar JSON con `jq . design-tokens.json` |
| Angular: NG_VALUE_ACCESSOR error | Verificar forwardRef + providers en Input/Select |
| Flutter: AppColors not found | Ejecutar `dart run tools/generate_tokens.dart` |
| flutter analyze errors | Revisar imports de shared_widgets.dart |
| Web build: UiButton not found | Verificar shared/ui/index.ts exports |
| Mobile: AppTextField validator null | Usar `validator: (v) => ...` no `validator: ...` |
| Deep link no abre app | Verificar AndroidManifest.xml intent-filter + `android:autoVerify="true"` |
| CU-19 AR no detecta pose | Verificar permisos cámara + `mobile/assets/images/garments/` existe |

---

## 📝 Archivos Clave a Modificar (Resumen)

### Frontend
- `design-tokens.json` (nuevo)
- `scripts/generate-tokens.js` (nuevo)
- `frontend/src/styles/design-system.css` (generado)
- `frontend/src/app/shared/ui/*` (12 componentes nuevos)
- `frontend/src/app/features/*/component.ts` (14 pantallas migradas)

### Mobile
- `design-tokens.json` (shared)
- `mobile/tools/generate_tokens.dart` (nuevo)
- `mobile/lib/core/design/design_tokens.dart` (generado)
- `mobile/lib/core/animation/app_animations.dart` (nuevo)
- `mobile/lib/core/design/app_theme.dart` (actualizar pageTransitions)
- `mobile/assets/images/empty/*.svg` (6 nuevos)
- `mobile/lib/features/promotions/promotions_screen.dart` (nuevo)
- `mobile/lib/features/catalog/catalog_routes.dart` (agregar ruta)
- 18 pantallas existentes (polish visual)

### Backend (Solo config - no código)
- `backend/.env` → RESEND_API_KEY, FROM_EMAIL (tú lo haces)
- `backend/app/services/email_service.py` → integración real (tú lo haces)

---

## 📌 Notas para el Ejecutor

1. **Orden estricto**: Fase 0 → 1 → 2 → 3 → 4 → 5. No saltar fases.
2. **CU-03 NO SE TOCA**: Solo UI visual en Forgot/Reset password web. Funcionalidad mock se mantiene.
3. **Email real**: Configuración externa (tú). No bloquea este plan.
4. **Testing real**: Usar device físico Android para CU-19 y notificaciones.
5. **Commits sugeridos**:
   - `feat(tokens): design-tokens.json + generators`
   - `feat(web): component library (12 components)`
   - `feat(web): polish 14 screens with new components`
   - `feat(mobile): polish 18 screens + CU-11 promotions`
   - `test(e2e): 34 CUs verified`
   - `chore: build verification`