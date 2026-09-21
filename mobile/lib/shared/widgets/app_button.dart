import 'package:flutter/material.dart';

import '../../core/design/design.dart';

enum AppButtonVariant { primary, secondary, outline, ghost, danger }

enum AppButtonSize { sm, md, lg, icon }

class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.size = AppButtonSize.md,
    this.loading = false,
    this.icon,
    this.expand = true,
    this.semanticLabel,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final AppButtonSize size;
  final bool loading;
  final bool expand;
  final IconData? icon;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final bg = isDark ? AppColors.darkSurfaceAlt : AppColors.surfaceAlt;

    final (fg, fill, border) = switch (variant) {
      AppButtonVariant.primary => (
          AppColors.primaryContrast,
          AppColors.primary,
          null,
        ),
      AppButtonVariant.secondary => (
          AppColors.primary,
          AppColors.primaryLight,
          null,
        ),
      AppButtonVariant.outline => (theme.colorScheme.onSurface, null, theme.colorScheme.outline),
      AppButtonVariant.ghost => (AppColors.primary, null, null),
      AppButtonVariant.danger => (AppColors.errorBg, AppColors.error, null),
    };

    final (height, hPad, fontSize, radius) = switch (size) {
      AppButtonSize.sm => (36.0, 12.0, 14.0, AppRadius.md),
      AppButtonSize.md => (48.0, 16.0, 15.0, AppRadius.md),
      AppButtonSize.lg => (56.0, 20.0, 16.0, AppRadius.md),
      AppButtonSize.icon => (48.0, 12.0, 15.0, AppRadius.md),
    };

    final style = ElevatedButton.styleFrom(
      backgroundColor: fill,
      foregroundColor: fg,
      elevation: 0,
      minimumSize: expand ? Size.fromHeight(height) : Size(0, height),
      padding: EdgeInsets.symmetric(horizontal: hPad, vertical: 0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(radius),
        side: border != null ? BorderSide(color: border) : BorderSide.none,
      ),
      disabledBackgroundColor: bg.withValues(alpha: 0.6),
      disabledForegroundColor: AppColors.textMuted,
      textStyle: theme.textTheme.labelLarge?.copyWith(
        fontSize: fontSize,
        fontWeight: FontWeight.w600,
      ),
    );

    return Semantics(
      button: true,
      label: semanticLabel ?? label,
      child: ElevatedButton(
        style: style,
        onPressed: loading ? null : onPressed,
        child: loading
            ? _loader(size: size, color: fg)
            : Row(
                mainAxisSize: expand ? MainAxisSize.max : MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: 18),
                    const SizedBox(width: 8),
                  ],
                  Flexible(
                    child: Text(
                      label,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _loader({required AppButtonSize size, required Color color}) {
    return SizedBox(
      width: size == AppButtonSize.sm ? 14 : 20,
      height: size == AppButtonSize.sm ? 14 : 20,
      child: CircularProgressIndicator(
        strokeWidth: 2,
        color: color,
      ),
    );
  }
}