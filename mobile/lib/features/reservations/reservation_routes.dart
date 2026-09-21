import 'package:go_router/go_router.dart';

import 'reservation_detail_screen.dart';
import 'reservations_screen.dart';

abstract class ReservationRoutes {
  static final routes = [
    GoRoute(
      path: '/reservations',
      builder: (context, state) => const ReservationsScreen(),
    ),
    GoRoute(
      path: '/reservations/:id',
      builder: (context, state) => ReservationDetailScreen(
        reservationId: int.parse(state.pathParameters['id']!),
      ),
    ),
  ];
}