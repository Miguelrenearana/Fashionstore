import 'package:go_router/go_router.dart';

import 'ar_fitting_screen.dart';

abstract class ArFittingRoutes {
  static const root = '/fitting/{variantId}';

  static final routes = [
    GoRoute(
      path: root,
      builder: (context, state) => ArFittingScreen(
        variantId: int.parse(state.pathParameters['variantId']!),
      ),
    ),
  ];
}