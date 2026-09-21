import 'package:flutter/material.dart';

import '../../core/design/design.dart';

enum AppStepStatus { completed, current, upcoming }

class AppStep {
  const AppStep({required this.label, this.icon});

  final String label;
  final IconData? icon;
}

class AppStepper extends StatelessWidget {
  const AppStepper({
    super.key,
    required this.steps,
    required this.currentStep,
    this.onStepTap,
  });

  final List<AppStep> steps;
  final int currentStep;
  final ValueChanged<int>? onStepTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: List.generate(steps.length * 2 - 1, (index) {
        if (index.isOdd) return const _StepperConnector();
        final stepIndex = index ~/ 2;
        return _StepperItem(
          step: steps[stepIndex],
          status: _status(stepIndex),
          isLast: stepIndex == steps.length - 1,
          theme: theme,
          onTap: onStepTap == null
              ? null
              : () => onStepTap!(stepIndex),
        );
      }),
    );
  }

  AppStepStatus _status(int index) {
    if (index < currentStep) return AppStepStatus.completed;
    if (index == currentStep) return AppStepStatus.current;
    return AppStepStatus.upcoming;
  }
}

class _StepperItem extends StatelessWidget {
  const _StepperItem({
    required this.step,
    required this.status,
    required this.isLast,
    required this.theme,
    this.onTap,
  });

  final AppStep step;
  final AppStepStatus status;
  final bool isLast;
  final ThemeData theme;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final (bg, fg) = switch (status) {
      AppStepStatus.completed => (AppColors.primary, Colors.white),
      AppStepStatus.current => (AppColors.primaryLight, AppColors.primaryDark),
      AppStepStatus.upcoming => (
          AppColors.surfaceAlt,
          AppColors.textMuted,
        ),
    };

    final circle = Container(
      width: 34,
      height: 34,
      decoration: BoxDecoration(
        color: bg,
        shape: BoxShape.circle,
        border: status == AppStepStatus.current
            ? Border.all(color: AppColors.primary, width: 2)
            : null,
      ),
      child: Icon(
        status == AppStepStatus.completed
            ? Icons.check
            : step.icon ?? Icons.circle,
        size: status == AppStepStatus.completed ? 16 : (step.icon != null ? 16 : 8),
        color: status == AppStepStatus.upcoming && step.icon == null
            ? AppColors.textMuted
            : fg,
      ),
    );

    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppRadius.md),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            circle,
            const SizedBox(height: AppSpacing.x2),
            Text(
              step.label,
              textAlign: TextAlign.center,
              style: theme.textTheme.labelSmall?.copyWith(
                color: status == AppStepStatus.current
                    ? AppColors.primary
                    : AppColors.textSecondary,
                fontWeight: status == AppStepStatus.current
                    ? FontWeight.w700
                    : FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StepperConnector extends StatelessWidget {
  const _StepperConnector();

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        height: 2,
        margin: const EdgeInsets.only(bottom: 22),
        color: AppColors.border,
      ),
    );
  }
}