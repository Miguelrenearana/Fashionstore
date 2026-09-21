import 'package:flutter/material.dart';

import '../../core/design/design.dart';

class AppCard extends StatelessWidget {
  const AppCard({
    super.key,
    this.child,
    this.onTap,
    this.hoverable = false,
    this.bordered = true,
    this.padding,
    this.margin,
    this.color,
    this.radius,
  });

  final Widget? child;
  final VoidCallback? onTap;
  final bool hoverable;
  final bool bordered;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Color? color;
  final double? radius;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final borderColor = isDark ? AppColors.darkBorder : AppColors.border;

    final borderRadius = BorderRadius.circular(radius ?? AppRadius.lg);
    final container = Container(
      margin: margin,
      padding: padding ?? const EdgeInsets.all(AppSpacing.x4),
      decoration: BoxDecoration(
        color: color ?? theme.colorScheme.surface,
        borderRadius: borderRadius,
        border: bordered ? Border.all(color: borderColor) : null,
        boxShadow: hoverable ? AppShadows.sm : null,
      ),
      child: child,
    );

    if (onTap == null) return container;

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: onTap,
        behavior: HitTestBehavior.opaque,
        child: container,
      ),
    );
  }
}