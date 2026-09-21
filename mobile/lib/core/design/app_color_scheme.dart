import 'package:flutter/material.dart';

import 'design_tokens.dart';

/// Light and dark [ColorScheme] built from the FashionStore design tokens.
abstract class AppColorScheme {
  static const ColorScheme light = ColorScheme(
    brightness: Brightness.light,
    primary: AppColors.primary,
    onPrimary: AppColors.primaryContrast,
    primaryContainer: AppColors.primaryLight,
    onPrimaryContainer: AppColors.primaryDark,
    secondary: AppColors.textSecondary,
    onSecondary: AppColors.textInverse,
    secondaryContainer: AppColors.surfaceAlt,
    onSecondaryContainer: AppColors.textMain,
    error: AppColors.error,
    onError: AppColors.textInverse,
    errorContainer: AppColors.errorBg,
    onErrorContainer: AppColors.error,
    surface: AppColors.surface,
    onSurface: AppColors.textMain,
    surfaceContainerHighest: AppColors.surfaceAlt,
    onSurfaceVariant: AppColors.textSecondary,
    outline: AppColors.border,
    outlineVariant: AppColors.border,
    shadow: Color(0xFF0F172A),
    scrim: Color(0x66000000),
    inverseSurface: AppColors.navBg,
    onInverseSurface: AppColors.textInverse,
    inversePrimary: AppColors.primaryLight,
    surfaceTint: AppColors.primary,
  );

  static const ColorScheme dark = ColorScheme(
    brightness: Brightness.dark,
    primary: AppColors.primary,
    onPrimary: AppColors.primaryContrast,
    primaryContainer: AppColors.primaryDark,
    onPrimaryContainer: AppColors.primaryLight,
    secondary: AppColors.textSecondary,
    onSecondary: AppColors.textInverse,
    secondaryContainer: AppColors.darkSurfaceAlt,
    onSecondaryContainer: AppColors.darkTextMain,
    error: AppColors.error,
    onError: AppColors.textInverse,
    errorContainer: Color(0xFF7F1D1D),
    onErrorContainer: AppColors.errorBg,
    surface: AppColors.darkSurface,
    onSurface: AppColors.darkTextMain,
    surfaceContainerHighest: AppColors.darkSurfaceAlt,
    onSurfaceVariant: AppColors.darkTextSecondary,
    outline: AppColors.darkBorder,
    outlineVariant: AppColors.darkBorder,
    shadow: Color(0xCC000000),
    scrim: Color(0x99000000),
    inverseSurface: AppColors.surface,
    onInverseSurface: AppColors.darkTextSecondary,
    inversePrimary: AppColors.primaryLight,
    surfaceTint: AppColors.primary,
  );
}