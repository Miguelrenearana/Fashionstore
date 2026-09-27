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
        state = state.copyWith(user: User.fromJson(res));
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
      final user = User.fromJson(userRes);
      
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

  /// CU-05: el alta de clientes es `POST /auth/register` (devuelve token).
  /// Antes se llamaba a `POST /users/`, que es el alta de personal y exige rol
  /// ADMIN, por lo que el registro desde la app respondia 403 siempre.
  Future<void> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final parts = _splitName(fullName);
      final res = await _api.post('/auth/register', data: {
        'email': email,
        'password': password,
        'first_name': parts.$1,
        'last_name': parts.$2,
      });
      // El registro ya devuelve un token utilizable: se guarda la sesion con el
      // en vez de pedir un segundo login.
      final token = res['access_token'] as String?;
      if (token != null) {
        await _api.setToken(token);
      }
      final userRes = await _api.get('/users/me');
      final user = User.fromJson(userRes);
      if (token != null) {
        await _api.saveSession(AuthSession(accessToken: token, user: user));
      }
      state = state.copyWith(user: user, isLoading: false);
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
      rethrow;
    }
  }

  /// El backend exige `first_name` y `last_name` por separado.
  static (String, String) _splitName(String fullName) {
    final clean = fullName.trim();
    final parts = clean.split(RegExp(r'\s+')).where((p) => p.isNotEmpty).toList();
    if (parts.isEmpty) return ('Cliente', 'Nuevo');
    if (parts.length == 1) return (parts.first, parts.first);
    return (parts.first, parts.sublist(1).join(' '));
  }

  Future<void> logout() async {
    await _api.clearSession();
    state = const AuthState();
  }

  /// CU-05: `PATCH /clients/me` recibe `first_name`/`last_name`/`phone` y
  /// devuelve el perfil del cliente plano (antes se leia `res['user']`).
  Future<void> updateProfile(User user) async {
    final parts = _splitName(user.fullName);
    final res = await _api.patch('/clients/me', data: {
      'first_name': parts.$1,
      'last_name': parts.$2,
      'phone': user.phone,
    });
    final profile = res['user'] as Map<String, dynamic>? ?? res;
    state = state.copyWith(
      user: User(
        id: user.id,
        email: profile['email'] as String? ?? user.email,
        fullName: [
          profile['first_name'] as String?,
          profile['last_name'] as String?,
        ].whereType<String>().where((p) => p.isNotEmpty).join(' '),
        role: user.role,
        phone: profile['phone'] as String?,
        avatarUrl: user.avatarUrl,
      ),
    );
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