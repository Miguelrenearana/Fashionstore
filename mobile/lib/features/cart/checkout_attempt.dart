import 'dart:math';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../../core/network/api_client.dart';

class CheckoutAttempt {
  const CheckoutAttempt(this.token, this.paymentMethod);

  final String token;
  final String paymentMethod;

  String encode() => '$token|$paymentMethod';

  static CheckoutAttempt? decode(String? value) {
    if (value == null) return null;
    final parts = value.split('|');
    if (parts.length != 2 || parts[0].isEmpty || parts[1].isEmpty) {
      throw const FormatException('Invalid saved checkout attempt');
    }
    return CheckoutAttempt(parts[0], parts[1]);
  }
}

abstract class CheckoutAttemptStore {
  Future<CheckoutAttempt?> read(int userId);
  Future<void> write(int userId, CheckoutAttempt attempt);
  Future<void> remove(int userId);
}

class SecureCheckoutAttemptStore implements CheckoutAttemptStore {
  const SecureCheckoutAttemptStore();

  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  String _key(int userId) => 'checkout_attempt:$userId';

  @override
  Future<CheckoutAttempt?> read(int userId) async =>
      CheckoutAttempt.decode(await _storage.read(key: _key(userId)));

  @override
  Future<void> write(int userId, CheckoutAttempt attempt) =>
      _storage.write(key: _key(userId), value: attempt.encode());

  @override
  Future<void> remove(int userId) => _storage.delete(key: _key(userId));
}

abstract class CheckoutPurchaseGateway {
  Future<Map<String, dynamic>> purchase(CheckoutAttempt attempt);
  Future<Map<String, dynamic>> recover(String token);
}

class ApiCheckoutPurchaseGateway implements CheckoutPurchaseGateway {
  ApiCheckoutPurchaseGateway(this.api);

  final ApiClient api;

  @override
  Future<Map<String, dynamic>> purchase(CheckoutAttempt attempt) =>
      api.post('/cart/purchase', data: {
        'payment_method': attempt.paymentMethod,
        'checkout_token': attempt.token,
      });

  @override
  Future<Map<String, dynamic>> recover(String token) =>
      api.get('/cart/purchase/$token');
}

/// A lost POST response never authorizes a fresh sale. A 404 from recovery
/// permits only a repeat of the same idempotent POST.
class CheckoutAttemptCoordinator {
  CheckoutAttemptCoordinator({
    required this.gateway,
    required this.store,
    required this.userId,
    String Function()? tokenFactory,
  }) : tokenFactory = tokenFactory ?? newCheckoutToken;

  final CheckoutPurchaseGateway gateway;
  final CheckoutAttemptStore store;
  final int userId;
  final String Function() tokenFactory;

  CheckoutAttempt? attempt;
  bool canRetry = false;

  Future<void> restore() async {
    attempt = await store.read(userId);
    canRetry = false;
  }

  Future<Map<String, dynamic>> start(String paymentMethod) async {
    if (attempt != null) throw StateError('Recover the existing purchase first');
    final next = CheckoutAttempt(tokenFactory(), paymentMethod);
    await store.write(userId, next); // Must succeed before any sale is created.
    attempt = next;
    return _submit(next);
  }

  Future<Map<String, dynamic>> recover() async {
    final current = attempt;
    if (current == null) throw StateError('No purchase to recover');
    canRetry = false;
    try {
      return await gateway.recover(current.token);
    } on ApiException catch (error) {
      canRetry = error.statusCode == 404;
      rethrow;
    }
  }

  Future<Map<String, dynamic>> retry() async {
    final current = attempt;
    if (current == null || !canRetry) {
      throw StateError('Recover the existing purchase before retrying');
    }
    canRetry = false;
    return _submit(current);
  }

  Future<Map<String, dynamic>> _submit(CheckoutAttempt current) async {
    try {
      return await gateway.purchase(current);
    } on ApiException catch (error) {
      // These are pre-sale validation failures. A transport or gateway error
      // leaves the outcome uncertain, so the token must remain recoverable.
      if (error.statusCode == 400 || error.statusCode == 422) {
        await reset();
      }
      rethrow;
    }
  }

  Future<void> reset() async {
    await store.remove(userId);
    attempt = null;
    canRetry = false;
  }
}

String newCheckoutToken() {
  final random = Random.secure();
  final bytes = List<int>.generate(16, (_) => random.nextInt(256));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  String hex(int from, int to) =>
      bytes.sublist(from, to).map((b) => b.toRadixString(16).padLeft(2, '0')).join();
  return '${hex(0, 4)}-${hex(4, 6)}-${hex(6, 8)}-${hex(8, 10)}-${hex(10, 16)}';
}
