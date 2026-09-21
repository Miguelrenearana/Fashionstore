import 'package:flutter/widgets.dart';

/// FashionStore Design Tokens
/// Generated from design-tokens.json (single source of truth)
/// Do not modify directly - update design-tokens.json and regenerate

class AppColors {
  // Primary
  static const primary = Color(0xFFFF8C00);
  static const primaryHover = Color(0xFFE67E00);
  static const primaryLight = Color(0xFFFFF3E0);
  static const primaryDark = Color(0xFFCC7000);
  static const primaryContrast = Color(0xFFFFFFFF);

  // Navigation
  static const navBg = Color(0xFF1A2B3A);
  static const navForeground = Color(0xFFFFFFFF);
  static const navMuted = Color(0xFF94A3B8);

  // Neutral
  static const background = Color(0xFFF5F7FA);
  static const surface = Color(0xFFFFFFFF);
  static const surfaceAlt = Color(0xFFF8FAFC);
  static const border = Color(0xFFE2E8F0);

  // Text
  static const textMain = Color(0xFF1E293B);
  static const textSecondary = Color(0xFF64748B);
  static const textMuted = Color(0xFF94A3B8);
  static const textInverse = Color(0xFFFFFFFF);

  // Semantic
  static const success = Color(0xFF059669);
  static const successBg = Color(0xFFECFDF5);
  static const warning = Color(0xFFD97706);
  static const warningBg = Color(0xFFFFFBEB);
  static const error = Color(0xFFDC2626);
  static const errorBg = Color(0xFFFEF2F2);
  static const info = Color(0xFF0284C7);
  static const infoBg = Color(0xFFF0F9FF);

  // Dark mode variants
  static const darkBackground = Color(0xFF0F172A);
  static const darkSurface = Color(0xFF1E293B);
  static const darkSurfaceAlt = Color(0xFF334155);
  static const darkBorder = Color(0xFF334155);
  static const darkTextMain = Color(0xFFF8FAFC);
  static const darkTextSecondary = Color(0xFF94A3B8);
  static const darkTextMuted = Color(0xFF64748B);
}

class AppSpacing {
  static const double x1 = 4.0;
  static const double x2 = 8.0;
  static const double x3 = 12.0;
  static const double x4 = 16.0;
  static const double x5 = 24.0;
  static const double x6 = 32.0;
  static const double x7 = 48.0;
  static const double x8 = 64.0;
}

class AppRadius {
  static const double sm = 4.0;
  static const double md = 8.0;
  static const double lg = 12.0;
  static const double full = 9999.0;
}

class AppShadows {
  static const List<BoxShadow> sm = [
    BoxShadow(
      color: Color(0x0D0F172A),
      offset: Offset(0, 1),
      blurRadius: 2,
      spreadRadius: 0,
    ),
  ];

  static const List<BoxShadow> md = [
    BoxShadow(
      color: Color(0x1A0F172A),
      offset: Offset(0, 4),
      blurRadius: 6,
      spreadRadius: -1,
    ),
    BoxShadow(
      color: Color(0x0D0F172A),
      offset: Offset(0, 2),
      blurRadius: 4,
      spreadRadius: -2,
    ),
  ];

  static const List<BoxShadow> lg = [
    BoxShadow(
      color: Color(0x1A0F172A),
      offset: Offset(0, 10),
      blurRadius: 15,
      spreadRadius: -3,
    ),
    BoxShadow(
      color: Color(0x100F172A),
      offset: Offset(0, 4),
      blurRadius: 6,
      spreadRadius: -4,
    ),
  ];

  static const List<BoxShadow> focus = [
    BoxShadow(
      color: Color(0x59FF8C00),
      offset: Offset(0, 0),
      blurRadius: 0,
      spreadRadius: 3,
    ),
  ];
}

class AppTypography {
  static const String fontFamily = 'Inter';
  static const String fontFamilyDisplay = 'Geist';

  static const TextStyle xs = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w400,
    height: 1.5,
    letterSpacing: 0.0,
  );

  static const TextStyle sm = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.5,
    letterSpacing: 0.0,
  );

  static const TextStyle base = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.5,
    letterSpacing: 0.0,
  );

  static const TextStyle lg = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w400,
    height: 1.5,
    letterSpacing: 0.0,
  );

  static const TextStyle xl = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w400,
    height: 1.4,
    letterSpacing: 0.0,
  );

  static const TextStyle xl2 = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    height: 1.3,
    letterSpacing: -0.01,
  );

  static const TextStyle xl3 = TextStyle(
    fontSize: 30,
    fontWeight: FontWeight.w600,
    height: 1.2,
    letterSpacing: -0.02,
  );

  static const TextStyle xl4 = TextStyle(
    fontSize: 36,
    fontWeight: FontWeight.w700,
    height: 1.1,
    letterSpacing: -0.025,
  );
}

class AppBreakpoints {
  static const double sm = 640;
  static const double md = 768;
  static const double lg = 1024;
  static const double xl = 1280;
  static const double xxl = 1536;
}

class AppZIndex {
  static const int dropdown = 1000;
  static const int sticky = 1020;
  static const int fixed = 1030;
  static const int modalBackdrop = 1040;
  static const int modal = 1050;
  static const int toast = 1080;
}