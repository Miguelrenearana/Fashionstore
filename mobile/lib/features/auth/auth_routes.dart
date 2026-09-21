import 'package:go_router/go_router.dart';

import 'forgot_password_screen.dart';
import 'login_screen.dart';
import 'register_screen.dart';
import 'reset_password_screen.dart';

abstract class AuthRoutes {
  static final routes = [
    GoRoute(
      path: '/auth/login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/auth/register',
      builder: (context, state) => const RegisterScreen(),
    ),
    GoRoute(
      path: '/auth/forgot',
      builder: (context, state) => const ForgotPasswordScreen(),
    ),
    GoRoute(
      path: '/auth/reset',
      builder: (context, state) => ResetPasswordScreen(
        token: state.uri.queryParameters['token'],
      ),
    ),
  ];
}