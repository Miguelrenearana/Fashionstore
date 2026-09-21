import 'package:flutter/material.dart';

import '../../core/design/design.dart';

class AppSelectOption {
  const AppSelectOption({
    required this.value,
    required this.label,
    this.disabled = false,
    this.icon,
  });

  final String value;
  final String label;
  final bool disabled;
  final IconData? icon;
}

class AppSelect extends StatelessWidget {
  const AppSelect({
    super.key,
    required this.options,
    this.value,
    this.label,
    this.placeholder,
    this.errorText,
    this.onChanged,
    this.defaultValue,
  });

  final List<AppSelectOption> options;
  final String? value;
  final String? defaultValue;
  final String? label;
  final String? placeholder;
  final String? errorText;
  final ValueChanged<String?>? onChanged;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final selected = options
        .where((o) => o.value == (value ?? defaultValue))
        .firstOrNull?.label;

    return DropdownButtonFormField<String>(
      initialValue: value ?? defaultValue,
      isExpanded: true,
      decoration: InputDecoration(
        labelText: label,
        errorText: errorText,
        prefixIcon: null,
      ),
      hint: Text(
        placementholder(selected, placeholder),
        style: theme.textTheme.bodyMedium
            ?.copyWith(color: AppColors.textMuted),
      ),
      items: options
          .map(
            (o) => DropdownMenuItem(
              value: o.value,
              enabled: !o.disabled,
              child: Row(
                children: [
                  if (o.icon != null) ...[
                    Icon(o.icon, size: 18, color: AppColors.textMuted),
                    const SizedBox(width: 8),
                  ],
                  Expanded(
                    child: Text(
                      o.label,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          )
          .toList(),
      onChanged: onChanged,
    );
  }

  String placementholder(String? selected, String? placeholder) {
    return selected ?? placeholder ?? 'Seleccionar';
  }
}

extension _FirstOrNull on Iterable<AppSelectOption> {
  AppSelectOption? get firstOrNull {
    final it = iterator;
    return it.moveNext() ? it.current : null;
  }
}