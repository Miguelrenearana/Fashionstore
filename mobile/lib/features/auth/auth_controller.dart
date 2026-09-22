import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/di/providers.dart';
import '../../core/models/models.dart';
import '../../core/network/api_client.dart';

class AuthState {
  const AuthState({
    this.user,
    this.isLoading = false,
    this.error,
  });

  final User? user;
  final bool isLoading;
  final String? error;

  bool get isAuthenticated => user != null;

  AuthState copyWith({User? user, bool? isLoading, String? error}) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._api) : super(const AuthState()) {
    _restoreSession();
  }

  final ApiClient _api;

  Future<void> _restoreSession() async {
    if (await _api.hasSession()) {
      try {
        final res = await _api.get('/users/me');
        state = state.copyWith(user: User.fromJson(res as Map<String, dynamic>));
      } catch (_) {
        await _api.clearSession();
      }
    }
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final form = FormData.fromMap({'username': email, 'password': password});
      final res = await _api.post('/auth/login', data: form);
      final accessToken = (res['access_token'] ?? res['token']) as String;
      
      // Guardar token PRIMERO para que el interceptor lo use en /users/me
      await _api.saveSession(AuthSession(
        accessToken: accessToken,
        refreshToken: res['refresh_token'] as String?,
        user: User(id: 0, email: email, fullName: '', role: 'client'),
      ));
      
      // Ahora obtener datos del usuario (el interceptor ya enviará el token)
      final userRes = await _api.get('/users/me');
      final user = User.fromJson(userRes as Map<String, dynamic>);
      
      // Actualizar sesión con datos reales del usuario
      await _api.saveSession(AuthSession(
        accessToken: accessToken,
        refreshToken: res['refresh_token'] as String?,
        user: user,
      ));
      state = state.copyWith(user: user, isLoading: false);
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
      rethrow;
    }
  }

  Future<void> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.post('/users/', data: {
        'email': email,
        'password': password,
        'full_name': fullName,
        'role': 'client',
      });
      final id = (res['id'] ?? 0) as int;
      state = state.copyWith(
        user: User(id: id, email: email, fullName: fullName, role: 'client'),
        isLoading: false,
      );
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
      rethrow;
    }
  }

  Future<void> logout() async {
    await _api.clearSession();
    state = const AuthState();
  }

  Future<void> updateProfile(User user) async {
    final res = await _api.patch('/clients/me', data: {
      'full_name': user.fullName,
      'phone': user.phone,
    });
    state = state.copyWith(user: User.fromJson(res['user'] as Map<String, dynamic>));
  }
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  return AuthController(ref.watch(apiClientProvider));
});

/// Wrapper que expone el estado de autenticación como [Listenable] para GoRouter
class AuthNotifier extends ChangeNotifier {
  AuthNotifier(this._ref) {
    _ref.listen<AuthState>(authControllerProvider, (_, next) {
      notifyListeners();
    });
  }

  final Ref _ref;

  AuthState get state => _ref.read(authControllerProvider);

  bool get isAuthenticated => state.isAuthenticated;
}

final authNotifierProvider = Provider<AuthNotifier>((ref) {
  return AuthNotifier(ref);
});