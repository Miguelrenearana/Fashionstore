import 'package:flutter/material.dart';

import '../../core/design/design.dart';

class AppTabs extends StatelessWidget {
  const AppTabs({
    super.key,
    required this.tabs,
    required this.controller,
    this.onChanged,
    this.labelStyle,
  });

  final List<String> tabs;
  final TabController controller;
  final ValueChanged<int>? onChanged;
  final TextStyle? labelStyle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return TabBar(
      controller: controller,
      onTap: onChanged,
      isScrollable: true,
      tabAlignment: TabAlignment.start,
      labelColor: AppColors.primaryDark,
      unselectedLabelColor: AppColors.textSecondary,
      labelStyle: labelStyle ??
          theme.textTheme.labelLarge?.copyWith(
            fontWeight: FontWeight.w600,
            fontSize: 14,
          ),
      unselectedLabelStyle: theme.textTheme.labelLarge?.copyWith(
        fontWeight: FontWeight.w500,
        fontSize: 14,
      ),
      indicatorColor: AppColors.primary,
      indicatorSize: TabBarIndicatorSize.label,
      dividerColor: Colors.transparent,
      labelPadding: const EdgeInsets.symmetric(horizontal: AppSpacing.x4),
      tabs: tabs.map((tab) => Tab(text: tab)).toList(),
    );
  }
}

class AppTabView extends StatelessWidget {
  const AppTabView({
    super.key,
    required this.controller,
    required this.children,
  });

  final TabController controller;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: TabBarView(
        controller: controller,
        children: children,
      ),
    );
  }
}