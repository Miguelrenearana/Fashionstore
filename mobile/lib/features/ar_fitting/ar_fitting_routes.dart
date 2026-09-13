import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'ar_fitting_screen.dart';

abstract class ArFittingRoutes {
  static const root = '/fitting/{variantId}';

  static final routes = [
    GoRoute(
      path: '/',
      builder: (context, state) => const PlaceholderScreen(),
    ),
    GoRoute(
      path: root,
      builder: (context, state) => ArFittingScreen(
        variantId: int.parse(state.pathParameters['variantId']!),
      ),
    ),
  ];
}

class PlaceholderScreen extends StatelessWidget {
  const PlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('FashionStore')),
      body: const Center(child: Text('Próximamente: catálogo y probador virtual')),
    );
  }
}