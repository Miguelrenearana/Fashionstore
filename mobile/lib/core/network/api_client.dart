import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../config/app_config.dart';
import '../models/models.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode, this.data,
    this.mayHaveReachedServer = true});

  final String message;
  final int? statusCode;
  final dynamic data;
  final bool mayHaveReachedServer;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient(this.config, {this.tokenReader, this.diagnostics,
    this.requestTimeout = const Duration(seconds: 45)});

  final AppConfig config;
  final Future<String?> Function()? tokenReader;
  final void Function(String)? diagnostics;
  final Duration requestTimeout;
  final Set<String> _creating = {};
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
          try {
            final token = await getToken().timeout(requestTimeout);
            if (options.cancelToken?.isCancelled ?? false) {
              handler.reject(DioException(requestOptions: options,
                type: DioExceptionType.cancel));
              return;
            }
            if (token != null && token.isNotEmpty) {
              options.headers['Authorization'] = 'Bearer $token';
            }
            final session = 'session=${token != null && token.isNotEmpty ? 'present' : 'absent'}';
            if (diagnostics != null) {
              diagnostics!(session);
            } else {
              debugPrint('FashionStore.http $session');
            }
            handler.next(options);
          } catch (_) {
            handler.reject(DioException(requestOptions: options,
              error: ApiException('No se pudo leer la sesión. Inicia sesión nuevamente.',
                mayHaveReachedServer: false)));
          }
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
    if (error.error is ApiException) {
      return error.error as ApiException;
    }
    final status = error.response?.statusCode;
    final data = error.response?.data;
    String message = status == 401
        ? 'Sesión no válida. Inicia sesión nuevamente.'
        : 'No se pudo conectar con el servidor. Comprueba tu conexión.';

    if (data is Map<String, dynamic>) {
      final detail = data['detail'] ?? data['message'];
      message = detail is String
          ? _humanize(detail)
          : (detail is List && detail.isNotEmpty)
              ? _extractValidationMessage(detail)
              : message;
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
      {Map<String, dynamic>? queryParameters}) =>
      _request('GET', path, queryParameters: queryParameters);

  /// GET that returns a top-level JSON list.
  Future<List<dynamic>> getList(String path,
      {Map<String, dynamic>? queryParameters}) =>
      _request('GET', path, queryParameters: queryParameters);

  Future<Map<String, dynamic>> post(String path,
      {Object? data, Map<String, dynamic>? queryParameters}) =>
      _request('POST', path, data: data, queryParameters: queryParameters);

  Future<Map<String, dynamic>> patch(String path,
      {Object? data}) => _request('PATCH', path, data: data);

  Future<Map<String, dynamic>> delete(String path,
      {Object? data}) => _request('DELETE', path, data: data);

  Future<T> _request<T>(String method, String path,
      {Object? data, Map<String, dynamic>? queryParameters}) async {
    final cancel = CancelToken();
    int? status;
    // No bodies, query values, identifiers, credentials or exception contents.
    final base = Uri.parse(config.apiBaseUrl);
    const publicSegments = {'', 'api', 'v1', 'cart', 'items', 'purchase',
      'checkout', 'reservations', 'me', 'status', 'locations', 'branches',
      'cities', 'catalog', 'categories', 'availability', 'auth', 'login',
      'register', 'users', 'payments', 'config', 'confirm', 'sales',
      'receipt', 'history'};
    final route = Uri.parse(path).path.split('/').map((part) =>
      publicSegments.contains(part) ? part : ':id').join('/');
    final label = '$method ${base.scheme}://${base.host}${base.hasPort ? ':${base.port}' : ''}${base.path}$route';
    void log(String result) {
      final message = '$label HTTP=${status ?? '-'} $result';
      if (diagnostics != null) {
        diagnostics!(message);
      } else {
        debugPrint('FashionStore.http $message');
      }
    }
    log('start');
    try {
      final res = await dio.request<dynamic>(path,
        options: Options(method: method), data: data,
        queryParameters: queryParameters, cancelToken: cancel,
      ).timeout(requestTimeout, onTimeout: () {
        cancel.cancel();
        throw TimeoutException('request deadline');
      });
      status = res.statusCode;
      final body = res.statusCode == 204 ? <String, dynamic>{} : res.data;
      if (body is! T) {
        log('invalid_response');
        throw ApiException('La API devolvió un formato inesperado.', statusCode: status);
      }
      log('ok');
      return body;
    } on DioException catch (e) {
      status = e.response?.statusCode;
      log(e.error is ApiException ? 'session_read_failed' : e.type.name);
      throw _parseError(e);
    } on TimeoutException {
      log('timeout');
      throw ApiException('La solicitud agotó el tiempo de espera. Comprueba tu conexión.');
    }
  }

  /// These endpoints increment/create and have no server idempotency key.
  /// Persist uncertainty per account before sending; a GET is not proof that
  /// a timed-out transaction will never commit, so it must not unlock a retry.
  Future<T> createOnce<T>(String path, {required Object data,
      required T Function(Map<String, dynamic>) decode}) async {
    if (!_creating.add(path)) {
      throw ApiException('Hay una solicitud en curso. Espera su resultado.');
    }
    try {
      final token = await getToken().timeout(requestTimeout);
      if (token == null) {
        throw ApiException('Inicia sesión para continuar.');
      }
      final claims = jsonDecode(utf8.decode(base64Url.decode(
        base64Url.normalize(token.split('.')[1])))) as Map<String, dynamic>;
      final subject = claims['sub'];
      if (subject == null) {
        throw ApiException('Inicia sesión nuevamente.');
      }
      final key = 'pending_creation_${base64Url.encode(utf8.encode('${config.apiBaseUrl}|$subject|$path'))}';
      final pending = await _storage.read(key: key).timeout(requestTimeout);
      const uncertain = 'Resultado sin confirmar. Consulta Carrito o Mis reservas y solicita verificar el intento antes de repetirlo. No se reenviará automáticamente.';
      if (pending != null) {
        throw ApiException(uncertain);
      }
      await _storage.write(key: key, value: 'pending').timeout(requestTimeout);
      try {
        final result = decode(await post(path, data: data));
        await _storage.delete(key: key).timeout(requestTimeout);
        return result;
      } catch (error) {
        if (error is ApiException && (!error.mayHaveReachedServer ||
            const [400, 401, 403, 404, 409, 422].contains(error.statusCode))) {
          await _storage.delete(key: key).timeout(requestTimeout);
          rethrow;
        }
        throw ApiException(uncertain);
      }
    } on ApiException {
      rethrow;
    } catch (_) {
      throw ApiException('No se pudo verificar la sesión o guardar el intento. Consulta tus operaciones antes de repetir.');
    } finally {
      _creating.remove(path);
    }
  }

  Future<void> saveSession(AuthSession session) async {
    await _storage.write(key: _tokenKey, value: session.accessToken);
    await _storage.write(key: _sessionKey, value: 'saved');
    if (session.refreshToken != null) {
      await _storage.write(key: 'auth_refresh_token', value: session.refreshToken);
    }
  }

  /// Guarda solo el token. Se usa tras el registro, cuando ya se tiene el token
  /// pero todavia no el usuario, y hace falta el token para pedir `/users/me`.
  Future<void> setToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
    await _storage.write(key: _sessionKey, value: 'saved');
  }

  Future<void> clearSession() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _sessionKey);
    await _storage.delete(key: 'auth_refresh_token');
  }

  Future<String?> getToken() => tokenReader?.call() ?? _storage.read(key: _tokenKey);
  Future<bool> hasSession() async {
    final token = await _storage.read(key: _tokenKey);
    return token != null && token.isNotEmpty;
  }
}
