import 'package:go_router/go_router.dart';

import 'notifications_screen.dart';
import 'profile_screen.dart';
import 'purchase_history_screen.dart';

abstract class ProfileRoutes {
  static final routes = [
    GoRoute(
      path: '/profile',
      builder: (context, state) => const ProfileScreen(),
    ),
    GoRoute(
      path: '/profile/orders',
      builder: (context, state) => const PurchaseHistoryScreen(),
    ),
    GoRoute(
      path: '/notifications',
      builder: (context, state) => const NotificationsScreen(),
    ),
  ];
}