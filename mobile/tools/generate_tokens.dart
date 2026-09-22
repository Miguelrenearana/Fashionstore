// GENERADOR AUTOMÁTICO DE DESIGN TOKENS
// Uso (desde mobile/): dart run tools/generate_tokens.dart
// Lee design-tokens.json (raíz del proyecto) y genera lib/core/design/design_tokens.dart

import 'dart:convert';
import 'dart:io';
import 'package:flutter/widgets.dart';

Map<String, dynamic> _readTokens() {
  final candidates = [
    File('design-tokens.json'),
    File('../design-tokens.json'),
  ];
  for (final f in candidates) {
    if (f.existsSync()) {
      return jsonDecode(f.readAsStringSync()) as Map<String, dynamic>;
    }
  }
  throw StateError('design-tokens.json no encontrado (busqué en mobile/ y raíz)');
}

String _camel(String s) {
  final parts = s.replaceAllMapped(
    RegExp(r'[A-Z]'),
    (m) => '_${m[0]!.toLowerCase()}',
  ).split('_');
  return parts.fold('', (acc, p) => acc + p[0].toUpperCase() + p.substring(1));
}

class _ShadowLayer {
  final double x, y, blur, spread;
  final int r, g, b;
  final double a;
  _ShadowLayer(this.x, this.y, this.blur, this.spread, this.r, this.g, this.b, this.a);
}

List<_ShadowLayer> _parseShadow(String css) {
  return css.split(', ').map((part) {
    final m = RegExp(r'^(-?\d+)[a-z%]*\s+(-?\d+)[a-z%]*\s+(-?\d+)[a-z%]*\s+(-?\d+)[a-z%]*\s+rgba?\(([\d.\s,]+)\)').firstMatch(part);
    if (m == null) {
      throw FormatException('Shadow no parseable: $part');
    }
    final rgba = m![5]!.split(',').map((e) => e.trim()).toList();
    return _ShadowLayer(
      double.parse(m[1]!),
      double.parse(m[2]!),
      double.parse(m[3]!),
      double.parse(m[4]!),
      int.parse(rgba[0]),
      int.parse(rgba[1]),
      int.parse(rgba[2]),
      double.parse(rgba[3]),
    );
  }).toList();
}

void main() {
  final t = _readTokens();
  final palette = t['palette'] as Map<String, dynamic>;
  final spacing = t['spacing'] as Map<String, dynamic>;
  final typography = t['typography'] as Map<String, dynamic>;
  final scale = typography['scale'] as Map<String, dynamic>;
  final zIndex = t['zIndex'] as Map<String, dynamic>;

  final b = StringBuffer()
    ..writeln('// GENERADO AUTOMÁTICAMENTE - NO EDITAR MANUALMENTE')
    ..writeln('// Fuente: design-tokens.json (single source of truth)')
    ..writeln('// Ejecutar: dart run tools/generate_tokens.dart')
    ..writeln('import \'package:flutter/widgets.dart\';')
    ..writeln('');

  // ============ AppColors ============
  b.writeln('class AppColors {');
  void color(String doc, String dartName, String hex) {
    b.writeln('  // $doc');
    b.writeln('  static const $dartName = Color(0x${hex.replaceFirst('#', 'FF')});');
  }

  b.writeln('  // Primary');
  final p = palette['primary'] as Map<String, dynamic>;
  color('', 'primary', p['default'] as String);
  color('', 'primaryHover', p['hover'] as String);
  color('', 'primaryLight', p['light'] as String);
  color('', 'primaryDark', p['dark'] as String);
  color('', 'primaryContrast', p['contrast'] as String);

  b.writeln('');
  b.writeln('  // Navigation');
  final nav = palette['nav'] as Map<String, dynamic>;
  color('', 'navBg', nav['bg'] as String);
  color('', 'navHover', nav['hover'] as String);
  color('', 'navForeground', nav['foreground'] as String);
  color('', 'navMuted', nav['muted'] as String);

  b.writeln('');
  b.writeln('  // Neutral');
  final neutral = palette['neutral'] as Map<String, dynamic>;
  color('', 'background', neutral['background'] as String);
  color('', 'surface', neutral['surface'] as String);
  color('', 'surfaceAlt', neutral['surfaceAlt'] as String);
  color('', 'border', neutral['border'] as String);

  b.writeln('');
  b.writeln('  // Text');
  final text = palette['text'] as Map<String, dynamic>;
  color('', 'textMain', text['main'] as String);
  color('', 'textSecondary', text['secondary'] as String);
  color('', 'textMuted', text['muted'] as String);
  color('', 'textInverse', text['inverse'] as String);

  b.writeln('');
  b.writeln('  // Semantic');
  final semantic = palette['semantic'] as Map<String, dynamic>;
  color('', 'success', semantic['success'] as String);
  color('', 'successBg', semantic['successBg'] as String);
  color('', 'warning', semantic['warning'] as String);
  color('', 'warningBg', semantic['warningBg'] as String);
  color('', 'error', semantic['error'] as String);
  color('', 'errorBg', semantic['errorBg'] as String);
  color('', 'info', semantic['info'] as String);
  color('', 'infoBg', semantic['infoBg'] as String);

  b.writeln('');
  b.writeln('  // Dark mode variants');
  b.writeln('  static const darkBackground = Color(0xFF0F172A);');
  b.writeln('  static const darkSurface = Color(0xFF1E293B);');
  b.writeln('  static const darkSurfaceAlt = Color(0xFF334155);');
  b.writeln('  static const darkBorder = Color(0xFF334155);');
  b.writeln('  static const darkTextMain = Color(0xFFF8FAFC);');
  b.writeln('  static const darkTextSecondary = Color(0xFF94A3B8);');
  b.writeln('  static const darkTextMuted = Color(0xFF64748B);');
  b.writeln('}');
  b.writeln('');

  // ============ AppSpacing ============
  b.writeln('class AppSpacing {');
  spacing.forEach((key, value) {
    final n = double.parse(value.replaceAll('px', ''));
    b.writeln('  static const double x$key = $n;');
  });
  b.writeln('}');
  b.writeln('');

  // ============ AppRadius ============
  b.writeln('class AppRadius {');
  final radius = t['radius'] as Map<String, dynamic>;
  radius.forEach((key, value) {
    final n = double.parse(value.replaceAll('px', ''));
    b.writeln('  static const double $key = $n;');
  });
  b.writeln('}');
  b.writeln('');

  // ============ AppShadows ============
  b.writeln('class AppShadows {');
  final shadows = t['shadows'] as Map<String, dynamic>;
  shadows.forEach((key, value) {
    final layers = _parseShadow(value as String);
    b.writeln('  static const List<BoxShadow> $key = [');
    for (final layer in layers) {
      b.writeln('    BoxShadow(');
      b.writeln('      color: Color.fromRGBO(${layer.r}, ${layer.g}, ${layer.b}, ${layer.a}),');
      b.writeln('      offset: Offset(${layer.x}, ${layer.y}),');
      b.writeln('      blurRadius: ${layer.blur},');
      b.writeln('      spreadRadius: ${layer.spread},');
      b.writeln('    ),');
    }
    b.writeln('  ];');
    b.writeln('');
  });
  b.writeln('}');
  b.writeln('');

  // ============ AppTypography ============
  b.writeln('class AppTypography {');
  b.writeln('  static const String fontFamily = \'Inter\';');
  b.writeln('  static const String fontFamilyDisplay = \'Geist\';');
  b.writeln('');
  const baseStyles = <String, ({double height, FontWeight weight, double letterSpacing})>{
    'xs': (height: 1.5, weight: FontWeight.w400, letterSpacing: 0.0),
    'sm': (height: 1.5, weight: FontWeight.w400, letterSpacing: 0.0),
    'base': (height: 1.5, weight: FontWeight.w400, letterSpacing: 0.0),
    'lg': (height: 1.5, weight: FontWeight.w400, letterSpacing: 0.0),
    'xl': (height: 1.4, weight: FontWeight.w400, letterSpacing: 0.0),
    '2xl': (height: 1.3, weight: FontWeight.w600, letterSpacing: -0.01),
    '3xl': (height: 1.2, weight: FontWeight.w600, letterSpacing: -0.02),
    '4xl': (height: 1.1, weight: FontWeight.w700, letterSpacing: -0.025),
  };
  final dartNames = {'2xl': 'xl2', '3xl': 'xl3', '4xl': 'xl4'};
  scale.forEach((key, value) {
    final size = double.parse(value.replaceAll('rem', '')).toStringAsFixed(1);
    final name = dartNames[key] ?? key;
    final style = baseStyles[key]!;
    b.writeln('  static const TextStyle $name = TextStyle(');
    b.writeln('    fontSize: $size,');
    b.writeln('    fontWeight: FontWeight.w${style.weight.index * 100},');
    b.writeln('    height: ${style.height},');
    b.writeln('    letterSpacing: ${style.letterSpacing},');
    b.writeln('  );');
    b.writeln('');
  });
  b.writeln('}');
  b.writeln('');

  // ============ AppBreakpoints ============
  b.writeln('class AppBreakpoints {');
  final breakpoints = t['breakpoints'] as Map<String, dynamic>;
  final bpNames = {'2xl': 'xxl'};
  breakpoints.forEach((key, value) {
    final n = double.parse(value.replaceAll('px', ''));
    final name = bpNames[key] ?? key;
    b.writeln('  static const double $name = $n;');
  });
  b.writeln('}');
  b.writeln('');

  // ============ AppZIndex ============
  b.writeln('class AppZIndex {');
  zIndex.forEach((key, value) {
    b.writeln('  static const int $key = $value;');
  });
  b.writeln('}');

  final outFile = File('lib/core/design/design_tokens.dart');
  outFile.writeAsStringSync(b.toString());
  stdout.writeln('OK design_tokens.dart generado (${outFile.path})');
}