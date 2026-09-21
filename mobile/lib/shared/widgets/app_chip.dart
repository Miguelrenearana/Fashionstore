import 'package:flutter/material.dart';

import '../../core/design/design.dart';

class AppChip extends StatelessWidget {
  const AppChip({
    super.key,
    required this.label,
    this.selected = false,
    this.enabled = true,
    this.removable = false,
    this.leading,
    this.onSelected,
    this.onRemoved,
  });

  final String label;
  final bool selected;
  final bool enabled;
  final bool removable;
  final Widget? leading;
  final ValueChanged<bool>? onSelected;
  final VoidCallback? onRemoved;

  @override
  Widget build(BuildContext context) {
    return InputChip(
      label: Text(label),
      selected: selected,
      onSelected: enabled ? onSelected : null,
      avatar: leading,
      deleteIcon: removable
          ? const Icon(Icons.close, size: 16)
          : null,
      onDeleted: removable && enabled ? onRemoved : null,
      showCheckmark: false,
      deleteButtonTooltipMessage: 'Quitar',
    );
  }
}

class AppChipSelector extends StatelessWidget {
  const AppChipSelector({
    super.key,
    required this.items,
    required this.selected,
    required this.onChanged,
    this.label,
    this.multiSelect = false,
  });

  final List<String> items;
  final Set<String> selected;
  final ValueChanged<Set<String>> onChanged;
  final String? label;
  final bool multiSelect;

  void _toggle(String item) {
    final next = Set<String>.from(selected);
    if (multiSelect) {
      if (next.contains(item)) {
        next.remove(item);
      } else {
        next.add(item);
      }
    } else {
      next
        ..clear()
        ..add(item);
    }
    onChanged(next);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null) ...[
          Text(
            label!,
            style: theme.textTheme.labelMedium
                ?.copyWith(color: AppColors.textSecondary),
          ),
          const SizedBox(height: AppSpacing.x2),
        ],
        Wrap(
          spacing: AppSpacing.x2,
          runSpacing: AppSpacing.x2,
          children: items
              .map(
                (item) => AppChip(
                  label: item,
                  selected: selected.contains(item),
                  onSelected: (_) => _toggle(item),
                ),
              )
              .toList(),
        ),
      ],
    );
  }
}