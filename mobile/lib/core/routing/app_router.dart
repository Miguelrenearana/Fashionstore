import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/ar_fitting/ar_fitting_routes.dart';
import '../../features/ai/ai_routes.dart';
import '../../features/auth/auth_controller.dart';
import '../../features/auth/auth_routes.dart';
import '../../features/cart/cart_routes.dart';
import '../../features/catalog/catalog_routes.dart';
import '../../features/profile/profile_routes.dart';
import '../../features/promotions/promotions_routes.dart';
import '../../features/reservations/reservation_routes.dart';
import '../../shared/widgets/app_shell.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _catalogKey = GlobalKey<NavigatorState>(debugLabel: 'catalog');
final _reservationsKey = GlobalKey<NavigatorState>(debugLabel: 'reservations');
final _cartKey = GlobalKey<NavigatorState>(debugLabel: 'cart');
final _aiKey = GlobalKey<NavigatorState>(debugLabel: 'ai');
final _profileKey = GlobalKey<NavigatorState>(debugLabel: 'profile');

final appRouterProvider = Provider<GoRouter>((ref) {
  final authNotifier = ref.watch(authNotifierProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/auth/login',
    refreshListenable: authNotifier,
    redirect: (context, state) {
      final isLoggedIn = authNotifier.isAuthenticated;
      final isAuthRoute = state.matchedLocation.startsWith('/auth/');
      final isArRoute = state.matchedLocation.startsWith('/ar/');
      final isPromoRoute = state.matchedLocation.startsWith('/promotions');

      // Allow access to auth, AR, and promotions routes without login
      if (isAuthRoute || isArRoute || isPromoRoute) {
        return null;
      }

      // If not logged in and trying to access protected routes, redirect to login
      if (!isLoggedIn) {
        return '/auth/login';
      }

      // If logged in and on login page, redirect to catalog
      if (isLoggedIn && isAuthRoute) {
        return '/catalog';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/',
        redirect: (context, state) => '/catalog',
      ),
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return MainShell(child: navigationShell);
        },
        branches: [
          StatefulShellBranch(
            navigatorKey: _catalogKey,
            routes: CatalogRoutes.routes,
          ),
          StatefulShellBranch(
            navigatorKey: _reservationsKey,
            routes: ReservationRoutes.routes,
          ),
          StatefulShellBranch(
            navigatorKey: _cartKey,
            routes: CartRoutes.routes,
          ),
          StatefulShellBranch(
            navigatorKey: _aiKey,
            routes: AiRoutes.routes,
          ),
          StatefulShellBranch(
            navigatorKey: _profileKey,
            routes: ProfileRoutes.routes,
          ),
        ],
      ),
      // Auth + AR + Promotions live on the root navigator (no bottom nav).
      ...AuthRoutes.routes,
      ...ArFittingRoutes.routes,
      ...PromotionsRoutes.routes,
    ],
  );
});