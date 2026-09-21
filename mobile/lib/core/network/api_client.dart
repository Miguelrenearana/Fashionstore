import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../config/app_config.dart';
import '../models/models.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode, this.data});

  final String message;
  final int? statusCode;
  final dynamic data;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient(this.config);

  final AppConfig config;
  final FlutterSecureStorage _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  static const _tokenKey = 'auth_access_token';
  static const _sessionKey = 'auth_session';

  late final Dio dio = _initDio();

  Dio _initDio() {
    final base = Dio(
      BaseOptions(
        baseUrl: config.apiBaseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 30),
        sendTimeout: const Duration(seconds: 15),
        headers: {'Accept': 'application/json'},
        validateStatus: (status) => status != null && status < 400,
      ),
    );

    base.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.read(key: _tokenKey);
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) {
          handler.next(error);
        },
      ),
    );
    return base;
  }

  /// Parses the error body or returns a generic message.
  ApiException _parseError(DioException error) {
    final status = error.response?.statusCode;
    final data = error.response?.data;
    String message = 'Error de conexión. Inténtalo de nuevo.';

    if (data is Map<String, dynamic>) {
      final detail = data['detail'];
      message = detail is String
          ? _humanize(detail)
          : (detail is List && detail.isNotEmpty)
              ? _extractValidationMessage(detail)
              : message;
    } else if (data is String && data.isNotEmpty) {
      message = data;
    }

    return ApiException(message, statusCode: status, data: data);
  }

  String _extractValidationMessage(List<dynamic> details) {
    final first = details.first;
    if (first is Map<String, dynamic>) {
      return '${first['msg'] ?? 'Datos inválidos'}';
    }
    return 'Datos inválidos';
  }

  String _humanize(String value) {
    final map = {
      'Incorrect username or password': 'Usuario o contraseña incorrectos',
      'User already exists': 'El usuario ya está registrado',
      'Invalid token': 'Sesión expirada. Inicia sesión nuevamente',
      'Email not verified': 'Correo no verificado',
      'Password reset token invalid': 'Código inválido o expirado',
    };
    return map[value] ?? value;
  }

  Future<Map<String, dynamic>> get(String path,
      {Map<String, dynamic>? queryParameters}) async {
    try {
      final res = await dio.get(path, queryParameters: queryParameters);
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _parseError(e);
    }
  }

  Future<Map<String, dynamic>> post(String path,
      {Object? data, Map<String, dynamic>? queryParameters}) async {
    try {
      final res =
          await dio.post(path, data: data, queryParameters: queryParameters);
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _parseError(e);
    }
  }

  Future<Map<String, dynamic>> patch(String path,
      {Object? data}) async {
    try {
      final res = await dio.patch(path, data: data);
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _parseError(e);
    }
  }

  Future<Map<String, dynamic>> delete(String path,
      {Object? data}) async {
    try {
      final res = await dio.delete(path, data: data);
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      if (e.response?.statusCode == 204 || e.response?.data == null) {
        return const {};
      }
      throw _parseError(e);
    }
  }

  Future<void> saveSession(AuthSession session) async {
    await _storage.write(key: _tokenKey, value: session.accessToken);
    await _storage.write(key: _sessionKey, value: 'saved');
    if (session.refreshToken != null) {
      await _storage.write(key: 'auth_refresh_token', value: session.refreshToken);
    }
  }

  Future<void> clearSession() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _sessionKey);
    await _storage.delete(key: 'auth_refresh_token');
  }

  Future<String?> getToken() => _storage.read(key: _tokenKey);
  Future<bool> hasSession() async {
    final token = await _storage.read(key: _tokenKey);
    return token != null && token.isNotEmpty;
  }
}