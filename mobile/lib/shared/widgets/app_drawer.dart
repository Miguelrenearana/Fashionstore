import 'package:flutter/material.dart';

import '../../core/design/design.dart';

class AppDrawerHeader extends StatelessWidget {
  const AppDrawerHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.logo,
    this.onClose,
  });

  final String title;
  final String? subtitle;
  final Widget? logo;
  final VoidCallback? onClose;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.navBg,
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.x4,
        AppSpacing.x4 + 8,
        AppSpacing.x4,
        AppSpacing.x5,
      ),
      child: Row(
        children: [
          if (logo != null) ...[
            logo!,
            const SizedBox(width: AppSpacing.x3),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: AppColors.navForeground,
                      ),
                ),
                if (subtitle != null)
                  Text(
                    subtitle!,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppColors.navMuted,
                        ),
                  ),
              ],
            ),
          ),
          if (onClose != null)
            IconButton(
              onPressed: onClose,
              icon: const Icon(Icons.close),
              color: AppColors.navForeground,
              tooltip: 'Cerrar',
            ),
        ],
      ),
    );
  }
}

class AppDrawerSection extends StatelessWidget {
  const AppDrawerSection({
    super.key,
    required this.title,
    required this.children,
  });

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(
        top: AppSpacing.x3,
        bottom: AppSpacing.x2,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.x4,
              vertical: AppSpacing.x2,
            ),
            child: Text(
              title.toUpperCase(),
              style: theme.textTheme.labelSmall
                  ?.copyWith(color: AppColors.textMuted),
            ),
          ),
          ...children,
        ],
      ),
    );
  }
}

class AppDrawerTile extends StatelessWidget {
  const AppDrawerTile({
    super.key,
    required this.icon,
    required this.label,
    this.selected = false,
    this.onTap,
    this.trailing,
  });

  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback? onTap;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        icon,
        color: selected ? AppColors.primary : AppColors.textSecondary,
      ),
      title: Text(
        label,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: selected ? AppColors.primary : null,
              fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
            ),
      ),
      trailing: trailing,
      selected: selected,
      selectedTileColor: AppColors.primaryLight,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppRadius.md),
      ),
      onTap: onTap,
    );
  }
}