import 'package:flutter_test/flutter_test.dart';

import 'package:fashionstore_mobile/core/network/api_client.dart';
import 'package:fashionstore_mobile/features/cart/checkout_attempt.dart';
import 'package:fashionstore_mobile/features/cart/checkout_screen.dart';

class MemoryStore implements CheckoutAttemptStore {
  final attempts = <int, CheckoutAttempt>{};

  @override
  Future<CheckoutAttempt?> read(int userId) async => attempts[userId];

  @override
  Future<void> write(int userId, CheckoutAttempt attempt) async {
    attempts[userId] = attempt;
  }

  @override
  Future<void> remove(int userId) async {
    attempts.remove(userId);
  }
}

class FakeGateway implements CheckoutPurchaseGateway {
  final sales = <String, Map<String, dynamic>>{};
  final postedTokens = <String>[];
  bool loseNextResponse = false;

  @override
  Future<Map<String, dynamic>> purchase(CheckoutAttempt attempt) async {
    postedTokens.add(attempt.token);
    final response = sales.putIfAbsent(attempt.token, () => {
      'sale': {'id': sales.length + 1, 'invoice_number': 'WEB-1', 'total_amount': 25},
      'payment': {'status': 'PENDING', 'gateway_reference': 'mock-ref-1'},
    });
    if (loseNextResponse) {
      loseNextResponse = false;
      throw ApiException('Connection lost');
    }
    return response;
  }

  @override
  Future<Map<String, dynamic>> recover(String token) async {
    final response = sales[token];
    if (response == null) throw ApiException('Not found', statusCode: 404);
    return response;
  }
}

void main() {
  const token1 = '84a89770-05c2-42c6-a96b-98da332c236e';
  const token2 = '960698a5-8647-4287-85c4-682ee530fc0a';

  test('lost POST response is recovered after restart without another sale', () async {
    final store = MemoryStore();
    final gateway = FakeGateway()..loseNextResponse = true;
    final first = CheckoutAttemptCoordinator(
      gateway: gateway, store: store, userId: 7, tokenFactory: () => token1,
    );
    await expectLater(first.start('static_qr'), throwsA(isA<ApiException>()));
    expect(store.attempts[7]!.token, token1);

    final restored = CheckoutAttemptCoordinator(
      gateway: gateway, store: store, userId: 7, tokenFactory: () => token2,
    );
    await restored.restore();
    await expectLater(restored.start('static_qr'), throwsStateError);
    final recovered = await restored.recover();
    expect(recovered['sale']['id'], 1);
    expect(isPaymentCompleted(OrderResult.fromJson(recovered).paymentStatus), isFalse);
    expect(gateway.postedTokens, [token1]);
    expect(gateway.sales, hasLength(1));
  });

  test('404 allows only a retry with the original token', () async {
    final store = MemoryStore();
    final gateway = FakeGateway();
    await store.write(7, const CheckoutAttempt(token1, 'card'));
    final attempt = CheckoutAttemptCoordinator(
      gateway: gateway, store: store, userId: 7, tokenFactory: () => token2,
    );
    await attempt.restore();
    await expectLater(attempt.retry(), throwsStateError);
    await expectLater(attempt.recover(), throwsA(isA<ApiException>()));
    expect(attempt.canRetry, isTrue);
    final response = await attempt.retry();
    expect(response['payment']['gateway_reference'], 'mock-ref-1');
    expect(gateway.postedTokens, [token1]);
    expect(gateway.sales, hasLength(1));
    await expectLater(attempt.retry(), throwsStateError);
  });

  test('attempts are isolated by user and reset permits a new token', () async {
    final store = MemoryStore();
    final gateway = FakeGateway();
    final owner = CheckoutAttemptCoordinator(
      gateway: gateway, store: store, userId: 7, tokenFactory: () => token1,
    );
    await owner.start('card');
    final other = CheckoutAttemptCoordinator(
      gateway: gateway, store: store, userId: 8, tokenFactory: () => token2,
    );
    await other.restore();
    expect(other.attempt, isNull);
    await owner.reset();
    expect(store.attempts[7], isNull);
    await other.start('card');
    expect(gateway.postedTokens, [token1, token2]);
  });

  test('a validation failure clears the attempt, a transport error keeps it', () async {
    final store = MemoryStore();
    final validation = _FailingGateway(422);
    final invalid = CheckoutAttemptCoordinator(
      gateway: validation, store: store, userId: 7, tokenFactory: () => token1,
    );
    await expectLater(invalid.start('card'), throwsA(isA<ApiException>()));
    expect(invalid.attempt, isNull);
    expect(store.attempts[7], isNull);

    final transport = _FailingGateway(null);
    final uncertain = CheckoutAttemptCoordinator(
      gateway: transport, store: store, userId: 7, tokenFactory: () => token2,
    );
    await expectLater(uncertain.start('card'), throwsA(isA<ApiException>()));
    expect(uncertain.attempt!.token, token2);
    expect(store.attempts[7]!.token, token2);
  });

  test('payment states never imply success before COMPLETED', () {
    for (final status in ['PENDING', 'DECLINED', 'TIMEOUT']) {
      final result = OrderResult.fromJson({
        'sale': {'id': 1, 'invoice_number': 'WEB-1', 'total_amount': 25},
        'payment': {'gateway_reference': 'mock-ref-1', 'status': status},
      });
      expect(result.saleId, 1);
      expect(result.reference, 'mock-ref-1');
      expect(isPaymentCompleted(result.paymentStatus), isFalse);
    }
    expect(isPaymentCompleted('COMPLETED'), isTrue);
    for (final status in ['PENDING', 'TIMEOUT', 'COMPLETED', null]) {
      expect(canStartNewPurchaseAfterPayment(status), isFalse);
    }
    expect(canStartNewPurchaseAfterPayment('DECLINED'), isTrue);
  });

  test('generated token is a UUID and corrupt saved state does not disappear', () {
    expect(newCheckoutToken(), matches(RegExp(
      r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    )));
    expect(() => CheckoutAttempt.decode('corrupt'), throwsFormatException);
  });
}

class _FailingGateway implements CheckoutPurchaseGateway {
  _FailingGateway(this.statusCode);

  final int? statusCode;

  @override
  Future<Map<String, dynamic>> purchase(CheckoutAttempt attempt) async =>
      throw ApiException('Failed', statusCode: statusCode);

  @override
  Future<Map<String, dynamic>> recover(String token) async =>
      throw ApiException('Failed', statusCode: statusCode);
}
