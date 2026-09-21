import 'package:flutter/material.dart';

import '../../core/design/design.dart';

enum AppBadgeVariant {
  default_, primary, success, warning, error, outline,
}

enum AppBadgeSize { sm, md }

class AppBadge extends StatelessWidget {
  const AppBadge({
    super.key,
    required this.label,
    this.variant = AppBadgeVariant.default_,
    this.size = AppBadgeSize.md,
    this.showDot = false,
    this.icon,
  });

  final String label;
  final AppBadgeVariant variant;
  final AppBadgeSize size;
  final bool showDot;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final (bg, fg) = switch (variant) {
      AppBadgeVariant.default_ => (
          isDark ? AppColors.darkSurfaceAlt : AppColors.surfaceAlt,
          theme.colorScheme.onSurface,
        ),
      AppBadgeVariant.primary => (AppColors.primaryLight, AppColors.primaryDark),
      AppBadgeVariant.success => (AppColors.successBg, AppColors.success),
      AppBadgeVariant.warning => (AppColors.warningBg, AppColors.warning),
      AppBadgeVariant.error => (AppColors.errorBg, AppColors.error),
      AppBadgeVariant.outline => (
          Colors.transparent,
          isDark ? AppColors.darkTextSecondary : AppColors.textSecondary,
        ),
    };

    final isSm = size == AppBadgeSize.sm;
    final dotSize = isSm ? 6.0 : 8.0;

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isSm ? AppSpacing.x2 : AppSpacing.x3,
        vertical: isSm ? 2 : AppSpacing.x1,
      ),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(AppRadius.full),
        border: variant == AppBadgeVariant.outline
            ? Border.all(color: AppColors.border)
            : null,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (showDot) ...[
            Container(
              width: dotSize,
              height: dotSize,
              decoration: BoxDecoration(
                color: fg,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 6),
          ],
          if (icon != null) ...[
            Icon(icon, size: isSm ? 12 : 14, color: fg),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(
              color: fg,
              fontWeight: FontWeight.w600,
              fontSize: isSm ? 10 : null,
            ),
          ),
        ],
      ),
    );
  }
}