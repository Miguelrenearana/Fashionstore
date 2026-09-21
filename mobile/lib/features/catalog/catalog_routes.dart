import 'package:go_router/go_router.dart';

import 'catalog_screen.dart';
import 'product_detail_screen.dart';

abstract class CatalogRoutes {
  static final routes = [
    GoRoute(
      path: '/catalog',
      builder: (context, state) => const CatalogScreen(),
    ),
    GoRoute(
      path: '/catalog/:id',
      builder: (context, state) => ProductDetailScreen(
        productId: int.parse(state.pathParameters['id']!),
      ),
    ),
  ];
}