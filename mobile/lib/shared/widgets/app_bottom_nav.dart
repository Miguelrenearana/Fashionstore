import 'package:flutter/material.dart';

import '../../core/design/design.dart';

class AppNavItem {
  const AppNavItem({
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.onTap,
    this.badgeCount,
  });

  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final VoidCallback onTap;
  final int? badgeCount;
}

class AppBottomNav extends StatelessWidget {
  const AppBottomNav({
    super.key,
    required this.items,
    required this.selectedIndex,
    this.color,
    this.onDestinationSelected,
  });

  final List<AppNavItem> items;
  final int selectedIndex;
  final Color? color;
  final ValueChanged<int>? onDestinationSelected;

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: selectedIndex,
      backgroundColor: Theme.of(context).colorScheme.surface,
      indicatorColor: AppColors.primaryLight,
      onDestinationSelected: (index) {
        onDestinationSelected?.call(index);
        items[index].onTap();
      },
      destinations: [
        for (var i = 0; i < items.length; i++)
          NavigationDestination(
            icon: Badge(
              isLabelVisible: items[i].badgeCount != null,
              label: items[i].badgeCount != null
                  ? Text('${items[i].badgeCount}')
                  : null,
              backgroundColor: AppColors.error,
              child: Icon(items[i].icon),
            ),
            selectedIcon: Badge(
              isLabelVisible: false,
              child: Icon(items[i].selectedIcon),
            ),
            label: items[i].label,
          ),
      ],
    );
  }
}