import 'package:flutter/material.dart';

import '../../core/design/design.dart';

class AppDropdownItem {
  const AppDropdownItem({
    required this.value,
    required this.label,
    this.icon,
    this.leading,
  });

  final String value;
  final String label;
  final IconData? icon;
  final Widget? leading;
}

class AppDropdown extends StatelessWidget {
  const AppDropdown({
    super.key,
    required this.items,
    required this.selected,
    required this.onChanged,
    this.alignment = Alignment.topRight,
    this.child,
  });

  final List<AppDropdownItem> items;
  final String selected;
  final ValueChanged<String> onChanged;
  final Alignment alignment;
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    final selectedItem = items.where((i) => i.value == selected).firstOrNull;

    return PopupMenuButton<String>(
      position: PopupMenuPosition.over,
      offset: const Offset(0, 48),
      color: Theme.of(context).colorScheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppRadius.md),
        side: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      menuPadding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.x1,
        vertical: AppSpacing.x1,
      ),
      onSelected: onChanged,
      itemBuilder: (context) => items
          .map(
            (item) => PopupMenuItem<String>(
              value: item.value,
              child: Row(
                children: [
                  if (item.leading != null) ...[
                    item.leading!,
                    const SizedBox(width: AppSpacing.x2),
                  ] else if (item.icon != null) ...[
                    Icon(
                      item.icon,
                      size: 18,
                      color: item.value == selected
                          ? AppColors.primary
                          : AppColors.textMuted,
                    ),
                    const SizedBox(width: AppSpacing.x2),
                  ],
                  Expanded(
                    child: Text(
                      item.label,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: item.value == selected
                                ? AppColors.primary
                                : null,
                            fontWeight: item.value == selected
                                ? FontWeight.w600
                                : FontWeight.w400,
                          ),
                    ),
                  ),
                  if (item.value == selected)
                    const Icon(
                      Icons.check,
                      size: 16,
                      color: AppColors.primary,
                    ),
                ],
              ),
            ),
          )
          .toList(),
      child: child ??
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.x3,
              vertical: AppSpacing.x2,
            ),
            decoration: BoxDecoration(
              border: Border.all(color: AppColors.border),
              borderRadius: BorderRadius.circular(AppRadius.md),
              color: Theme.of(context).colorScheme.surface,
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  selectedItem?.label ?? 'Seleccionar',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(width: AppSpacing.x1),
                const Icon(
                  Icons.arrow_drop_down,
                  size: 20,
                  color: AppColors.textMuted,
                ),
              ],
            ),
          ),
    );
  }
}

extension _FirstOrNullSel on Iterable<AppDropdownItem> {
  AppDropdownItem? get firstOrNull {
    final it = iterator;
    return it.moveNext() ? it.current : null;
  }
}