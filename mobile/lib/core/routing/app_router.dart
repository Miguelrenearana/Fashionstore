import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/ar_fitting/ar_fitting_routes.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    routes: ArFittingRoutes.routes,
  );
});