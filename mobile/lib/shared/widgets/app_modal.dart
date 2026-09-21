import 'package:flutter/material.dart';

import '../../core/design/design.dart';

enum AppModalSize { auto, sm, md, lg }

class AppModal extends StatelessWidget {
  const AppModal({
    super.key,
    required this.child,
    this.title,
    this.subtitle,
    this.size = AppModalSize.auto,
    this.actions,
    this.showClose = true,
  });

  final Widget child;
  final String? title;
  final String? subtitle;
  final AppModalSize size;
  final List<Widget>? actions;
  final bool showClose;

  Future<void> show(BuildContext context) {
    return showDialog<void>(
      context: context,
      builder: (_) => this,
    );
  }

  double get _maxWidth => switch (size) {
        AppModalSize.auto => 480,
        AppModalSize.sm => 360,
        AppModalSize.md => 480,
        AppModalSize.lg => 720,
      };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Dialog(
      insetPadding: const EdgeInsets.all(AppSpacing.x4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppRadius.lg),
      ),
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: _maxWidth),
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.x5),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (title != null) ...[
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          title!,
                          style: theme.textTheme.headlineSmall,
                        ),
                      ),
                      if (showClose)
                        IconButton(
                          onPressed: () => Navigator.of(context).pop(),
                          icon: const Icon(Icons.close),
                          tooltip: 'Cerrar',
                        ),
                    ],
                  ),
                  if (subtitle != null) ...[
                    const SizedBox(height: AppSpacing.x1),
                    Text(
                      subtitle!,
                      style: theme.textTheme.bodyMedium
                          ?.copyWith(color: AppColors.textSecondary),
                    ),
                  ],
                  const SizedBox(height: AppSpacing.x4),
                ],
                child,
                if (actions != null) ...[
                  const SizedBox(height: AppSpacing.x5),
                  Wrap(
                    spacing: AppSpacing.x2,
                    runSpacing: AppSpacing.x2,
                    alignment: WrapAlignment.end,
                    children: actions!,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}