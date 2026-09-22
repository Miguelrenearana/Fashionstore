import 'package:go_router/go_router.dart';

import 'promotions_screen.dart';

/// Ruta CU-11 (promociones activas). Vive en el root navigator,
/// accesible desde el catálogo u otras secciones, sin bottom nav.
abstract class PromotionsRoutes {
  static final routes = [
    GoRoute(
      path: '/promotions',
      builder: (context, state) => const PromotionsScreen(),
    ),
  ];
}
