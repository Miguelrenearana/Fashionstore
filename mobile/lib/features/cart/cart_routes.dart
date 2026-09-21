import 'package:go_router/go_router.dart';

import 'cart_screen.dart';
import 'checkout_screen.dart';

abstract class CartRoutes {
  static final routes = [
    GoRoute(
      path: '/cart',
      builder: (context, state) => const CartScreen(),
    ),
    GoRoute(
      path: '/checkout',
      builder: (context, state) => const CheckoutScreen(),
    ),
  ];
}