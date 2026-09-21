import 'package:go_router/go_router.dart';

import 'ai_chat_screen.dart';
import 'recommendations_screen.dart';

abstract class AiRoutes {
  static final routes = [
    GoRoute(
      path: '/recommendations',
      builder: (context, state) => const RecommendationsScreen(),
    ),
    GoRoute(
      path: '/ai/chat',
      builder: (context, state) => const AIChatScreen(),
    ),
  ];
}