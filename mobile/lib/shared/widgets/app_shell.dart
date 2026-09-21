import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'app_bottom_nav.dart';

class MainShell extends StatefulWidget {
  const MainShell({super.key, required this.child, this.currentIndex = 0});

  final Widget child;
  final int currentIndex;

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: widget.child,
      bottomNavigationBar: AppBottomNav(
        selectedIndex: widget.currentIndex,
        items: [
          AppNavItem(
            icon: Icons.storefront_outlined,
            selectedIcon: Icons.storefront,
            label: 'Inicio',
            onTap: () => context.go('/catalog'),
          ),
          AppNavItem(
            icon: Icons.shopping_bag_outlined,
            selectedIcon: Icons.shopping_bag,
            label: 'Reservas',
            onTap: () => context.go('/reservations'),
          ),
          AppNavItem(
            icon: Icons.shopping_cart_outlined,
            selectedIcon: Icons.shopping_cart,
            label: 'Carrito',
            onTap: () => context.go('/cart'),
          ),
          AppNavItem(
            icon: Icons.smart_toy_outlined,
            selectedIcon: Icons.smart_toy,
            label: 'IA',
            onTap: () => context.go('/recommendations'),
          ),
          AppNavItem(
            icon: Icons.person_outline,
            selectedIcon: Icons.person,
            label: 'Perfil',
            onTap: () => context.go('/profile'),
          ),
        ],
      ),
    );
  }
}

class MainRouteShell extends StatelessWidget {
  const MainRouteShell({super.key, this.index = 0, required this.child});

  final Widget child;
  final int index;

  @override
  Widget build(BuildContext context) {
    return MainShell(currentIndex: index, child: child);
  }
}