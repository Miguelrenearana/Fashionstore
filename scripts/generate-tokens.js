'use strict';
// Genera frontend/src/styles/design-system.css desde design-tokens.json
// Uso: node scripts/generate-tokens.js

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const tokensPath = path.join(root, 'design-tokens.json');
const tokens = JSON.parse(fs.readFileSync(tokensPath, 'utf8'));

const palette = tokens.palette;
const spacing = tokens.spacing;
const radius = tokens.radius;
const typography = tokens.typography;
const shadows = tokens.shadows;
const transitions = tokens.transition;
const zIndex = tokens.zIndex;

const lines = [];
lines.push(':root {');

// ============ BRAND ============
lines.push('  /* === BRAND === */');
lines.push(`  --color-primary: ${palette.primary.default};`);
lines.push(`  --color-primary-hover: ${palette.primary.hover};`);
lines.push(`  --color-primary-light: ${palette.primary.light};`);
lines.push(`  --color-primary-dark: ${palette.primary.dark};`);
lines.push('');

// ============ NAV / SURFACES ============
lines.push('  /* === NAV / SURFACES === */');
lines.push(`  --color-nav: ${palette.nav.bg};`);
lines.push(`  --color-nav-hover: ${palette.nav.hover};`);
lines.push(`  --color-nav-muted: ${palette.nav.muted};`);
lines.push(`  --color-surface: ${palette.neutral.surface};`);
lines.push(`  --color-surface-alt: ${palette.neutral.surfaceAlt};`);
lines.push(`  --color-bg: ${palette.neutral.background};`);
lines.push('');

// ============ TEXT ============
lines.push('  /* === TEXT === */');
lines.push(`  --color-text: ${palette.text.main};`);
lines.push(`  --color-text-secondary: ${palette.text.secondary};`);
lines.push(`  --color-text-muted: ${palette.text.muted};`);
lines.push(`  --color-text-on-primary: ${palette.primary.contrast};`);
lines.push(`  --color-text-on-nav: ${palette.nav.foreground};`);
lines.push('');

// ============ BORDERS ============
lines.push('  /* === BORDERS === */');
lines.push(`  --color-border: ${palette.neutral.border};`);
lines.push(`  --color-border-focus: ${palette.primary.default};`);
lines.push('');

// ============ SEMANTIC ============
lines.push('  /* === SEMANTIC === */');
lines.push(`  --color-success: ${palette.semantic.success};`);
lines.push(`  --color-success-light: ${palette.semantic.successBg};`);
lines.push(`  --color-warning: ${palette.semantic.warning};`);
lines.push(`  --color-warning-light: ${palette.semantic.warningBg};`);
lines.push(`  --color-error: ${palette.semantic.error};`);
lines.push(`  --color-error-light: ${palette.semantic.errorBg};`);
lines.push(`  --color-info: ${palette.semantic.info};`);
lines.push(`  --color-info-light: ${palette.semantic.infoBg};`);
lines.push('');

// ============ SPACING ============
lines.push('  /* === SPACING === */');
Object.entries(spacing).forEach(([key, value]) => {
  lines.push(`  --space-${key}: ${value};`);
});
lines.push('');

// ============ TYPOGRAPHY ============
lines.push('  /* === TYPOGRAPHY === */');
lines.push(`  --font-sans: ${typography.fontFamily};`);
lines.push(`  --font-display: ${typography.fontFamilyDisplay};`);
Object.entries(typography.scale).forEach(([key, value]) => {
  lines.push(`  --text-${key}: ${value};`);
});
lines.push('');

// ============ RADIUS ============
lines.push('  /* === RADIUS === */');
Object.entries(radius).forEach(([key, value]) => {
  lines.push(`  --radius-${key}: ${value};`);
});
lines.push('');

// ============ SHADOWS ============
lines.push('  /* === SHADOWS === */');
Object.entries(shadows).forEach(([key, value]) => {
  lines.push(`  --shadow-${key}: ${value};`);
});
lines.push('');

// ============ TRANSITIONS ============
lines.push('  /* === TRANSITIONS === */');
Object.entries(transitions).forEach(([key, value]) => {
  lines.push(`  --transition-${key}: ${value};`);
});
lines.push('');

// ============ Z-INDEX ============
lines.push('  /* === Z-INDEX === */');
Object.entries(zIndex).forEach(([key, value]) => {
  const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
  lines.push(`  --z-${cssKey}: ${value};`);
});
lines.push('}');

// ============ DARK MODE ============
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
  'shadow-sm': '0 1px 2px rgba(0, 0, 0, 0.3)',
  'shadow-md': '0 4px 6px rgba(0, 0, 0, 0.4)',
  'shadow-lg': '0 10px 15px rgba(0, 0, 0, 0.5)',
};
lines.push('');
lines.push('@media (prefers-color-scheme: dark) {');
lines.push('  :root {');
Object.entries(darkOverrides).forEach(([k, v]) => {
  lines.push(`    --${k}: ${v};`);
});
lines.push('  }');
lines.push('}');

const output = lines.join('\n') + '\n';
const outPath = path.join(root, 'frontend/src/styles/design-system.css');
fs.writeFileSync(outPath, output);
console.log('OK design-system.css generado (' + outPath + ')');