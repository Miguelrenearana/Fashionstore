import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:fashionstore_mobile/core/config/app_config.dart';
import 'package:fashionstore_mobile/core/di/providers.dart';
import 'package:fashionstore_mobile/core/models/models.dart';
import 'package:fashionstore_mobile/core/network/api_client.dart';
import 'package:fashionstore_mobile/features/cart/cart_controller.dart';
import 'package:fashionstore_mobile/features/cart/cart_screen.dart';
import 'package:fashionstore_mobile/features/catalog/product_detail_screen.dart';
import 'package:fashionstore_mobile/features/reservations/reservation_controller.dart';
import 'package:fashionstore_mobile/features/reservations/reservations_screen.dart';

class MemoryAdapter implements HttpClientAdapter {
  MemoryAdapter(this.respond);
  final Future<ResponseBody> Function(RequestOptions) respond;
  final List<RequestOptions> requests = [];

  @override
  Future<ResponseBody> fetch(RequestOptions options,
      Stream<Uint8List>? requestStream, Future<void>? cancelFuture) {
    requests.add(options);
    return respond(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody jsonResponse(Object body, [int status = 200]) =>
    ResponseBody.fromString(jsonEncode(body), status,
      headers: {Headers.contentTypeHeader: ['application/json']});

String tokenFor(String subject) =>
    'header.${base64Url.encode(utf8.encode(jsonEncode({'sub': subject})))}.signature';

ApiClient client(MemoryAdapter adapter, {String subject = 'test-client',
    Future<String?> Function()? tokenReader, List<String>? logs,
    Duration timeout = const Duration(seconds: 2)}) {
  final api = ApiClient(const AppConfig(apiBaseUrl: 'https://test.invalid/api/v1'),
    tokenReader: tokenReader ?? () async => tokenFor(subject),
    diagnostics: (message) => logs?.add(message), requestTimeout: timeout);
  api.dio.httpClientAdapter = adapter;
  return api;
}

const emptyCart = {'id': 1, 'details': <Object>[], 'total': 0};
const fullCart = {'id': 1, 'total': 30, 'details': [
  {'variant_id': 7, 'garment_id': 3, 'garment_name': 'Camisa',
    'quantity': 2, 'unit_price': 15, 'size_name': 'M', 'color_name': 'Azul'},
]};
const reservation = {'id': 9, 'status': 'PENDING', 'branch_id': 2,
  'branch_name': 'Centro', 'total_amount': 30, 'details': [
    {'variant_id': 7, 'quantity': 2, 'unit_price': 15},
  ]};
const item = CartItem(variantId: 7, productId: 3, name: 'Camisa', price: 15,
  quantity: 2);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));

  test('reservations consume a JSON list and always close loading on bad data', () async {
    Object body = [reservation];
    final adapter = MemoryAdapter((_) async => jsonResponse(body));
    final controller = ReservationController(client(adapter));
    addTearDown(controller.dispose);
    await controller.load();
    expect(controller.state.reservations.single.id, 9);
    expect(controller.state.isLoading, isFalse);
    body = [{'id': 'invalid'}];
    await controller.load();
    expect(controller.state.isLoading, isFalse);
    expect(controller.state.error, isNotNull);
    body = [reservation];
    await controller.load();
    expect(controller.state.error, isNull);
  });

  test('cart bad JSON closes loading; retry loads server details', () async {
    Object body = {'details': 'invalid', 'total': 0};
    final controller = CartController(client(MemoryAdapter((_) async => jsonResponse(body))));
    addTearDown(controller.dispose);
    await controller.load();
    expect(controller.state.isLoading, isFalse);
    expect(controller.state.error, isNotNull);
    body = fullCart;
    await controller.load();
    expect(controller.state.items.single.variantId, 7);
    expect(controller.state.total, 30);
    expect(controller.state.error, isNull);
  });

  test('add sends selected variant/quantity, consumes response and prevents overlap', () async {
    final reply = Completer<ResponseBody>();
    final adapter = MemoryAdapter((options) async => options.method == 'POST'
      ? reply.future : jsonResponse(emptyCart));
    final controller = CartController(client(adapter));
    addTearDown(controller.dispose);
    await controller.load();
    final countBefore = adapter.requests.length;
    final adding = controller.addItem(item);
    await expectLater(controller.addItem(item), throwsA(isA<ApiException>()));
    reply.complete(jsonResponse(fullCart));
    await adding;
    final requests = adapter.requests.skip(countBefore).toList();
    expect(requests, hasLength(1));
    expect(requests.single.method, 'POST');
    expect(requests.single.path, '/cart/items');
    expect(requests.single.data, {'variant_id': 7, 'quantity': 2});
    expect(requests.single.headers['Authorization'], 'Bearer ${tokenFor('test-client')}');
    expect(controller.state.items.single.quantity, 2);
    expect(controller.state.isLoading, isFalse);
  });

  test('reservation uses branch and publishes confirmed record without a second GET', () async {
    final adapter = MemoryAdapter((o) async => jsonResponse(o.method == 'POST' ? reservation : []));
    final controller = ReservationController(client(adapter));
    addTearDown(controller.dispose);
    await controller.load();
    final before = adapter.requests.length;
    await controller.create(items: [{'variant_id': 7, 'quantity': 2}], branchId: 2);
    final requests = adapter.requests.skip(before).toList();
    expect(requests, hasLength(1));
    expect(requests.single.data, {'branch_id': 2,
      'items': [{'variant_id': 7, 'quantity': 2}]});
    expect(controller.state.reservations.single.id, 9);
  });

  test('quantity PATCH includes variant_id required by API', () async {
    final adapter = MemoryAdapter((_) async => jsonResponse(fullCart));
    final controller = CartController(client(adapter));
    addTearDown(controller.dispose);
    await controller.load();
    await controller.updateQuantity(7, 2);
    expect(adapter.requests.last.data, {'variant_id': 7, 'quantity': 2});
    expect(controller.state.error, isNull);
  });

  for (final path in ['/cart/items', '/reservations']) {
    test('$path lost response persists across clients, isolates accounts and never resends', () async {
      var creates = 0;
      final adapter = MemoryAdapter((o) async {
        creates++;
        throw DioException(requestOptions: o, type: DioExceptionType.receiveTimeout);
      });
      Future<void> create(ApiClient api) async {
        await api.createOnce(path, data: const {'variant_id': 7}, decode: (r) => r);
      }
      await expectLater(create(client(adapter)), throwsA(isA<ApiException>()));
      await expectLater(create(client(adapter)), throwsA(isA<ApiException>()));
      expect(creates, 1);
      await expectLater(create(client(adapter, subject: 'another-client')),
        throwsA(isA<ApiException>()));
      expect(creates, 2);
    });
  }

  test('uncertain reservation creation consults the backend without another POST', () async {
    var created = false;
    final adapter = MemoryAdapter((o) async {
      if (o.method == 'POST') {
        created = true;
        throw DioException(requestOptions: o, type: DioExceptionType.receiveTimeout);
      }
      return jsonResponse(created ? [reservation] : []);
    });
    final controller = ReservationController(client(adapter));
    addTearDown(controller.dispose);
    await controller.load();
    await expectLater(controller.create(items: [{'variant_id': 7, 'quantity': 2}],
      branchId: 2), throwsA(isA<ApiException>()));
    expect(controller.state.reservations.single.id, 9);
    expect(controller.state.isLoading, isFalse);
    expect(adapter.requests.where((o) => o.method == 'POST'), hasLength(1));
    expect(adapter.requests.last.path, '/reservations/me');
  });

  test('validation failure is visible and allows corrected creation', () async {
    var attempt = 0;
    final api = client(MemoryAdapter((_) async => ++attempt == 1
      ? jsonResponse({'message': 'Stock insuficiente', 'detail': null}, 422)
      : jsonResponse(reservation)));
    await expectLater(api.createOnce('/reservations', data: const {}, decode: (r) => r),
      throwsA(isA<ApiException>().having((e) => e.message, 'message', 'Stock insuficiente')));
    final result = await api.createOnce('/reservations', data: const {}, decode: (r) => r);
    expect(result['id'], 9);
  });

  test('invalid success body remains uncertain and is not posted again', () async {
    var writes = 0;
    final api = client(MemoryAdapter((_) async {
      writes++;
      return jsonResponse({'unexpected': 'response'});
    }));
    Future<int> create() => api.createOnce('/reservations', data: const {},
      decode: (body) => body['id'] as int);
    await expectLater(create(), throwsA(isA<ApiException>()));
    await expectLater(create(), throwsA(isA<ApiException>()));
    expect(writes, 1);
  });

  test('confirmed creation clears marker for an intentional new operation', () async {
    var writes = 0;
    final api = client(MemoryAdapter((_) async {
      writes++;
      return jsonResponse(reservation);
    }));
    for (var i = 0; i < 2; i++) {
      final result = await api.createOnce('/reservations', data: const {},
        decode: (body) => body['id'] as int);
      expect(result, 9);
    }
    expect(writes, 2);
  });

  test('lost cart response reads back applied quantity without adding it twice', () async {
    var applied = false;
    final adapter = MemoryAdapter((o) async {
      if (o.method == 'POST') {
        applied = true;
        throw DioException(requestOptions: o, type: DioExceptionType.receiveTimeout);
      }
      return jsonResponse(applied ? fullCart : emptyCart);
    });
    final controller = CartController(client(adapter));
    addTearDown(controller.dispose);
    await controller.load();
    await expectLater(controller.addItem(item), throwsA(isA<ApiException>()));
    expect(controller.state.items.single.quantity, 2);
    expect(controller.state.isLoading, isFalse);
    await expectLater(controller.addItem(item), throwsA(isA<ApiException>()));
    expect(adapter.requests.where((o) => o.method == 'POST'), hasLength(1));
    expect(adapter.requests.last.path, '/cart');
  });

  test('secure storage failure rejects interceptor without a network request', () async {
    final adapter = MemoryAdapter((_) async => jsonResponse(emptyCart));
    final api = client(adapter, tokenReader: () async => throw StateError('secret'));
    await expectLater(api.get('/cart'), throwsA(isA<ApiException>()));
    expect(adapter.requests, isEmpty);
  });

  test('unresolved token read reaches deadline and never sends late request', () async {
    final token = Completer<String?>();
    final adapter = MemoryAdapter((_) async => jsonResponse(emptyCart));
    final api = client(adapter, tokenReader: () => token.future,
      timeout: const Duration(milliseconds: 20));
    await expectLater(api.get('/cart'), throwsA(isA<ApiException>()));
    token.complete(tokenFor('test-client'));
    await Future<void>.delayed(const Duration(milliseconds: 30));
    expect(adapter.requests, isEmpty);
  });

  test('diagnostics contain route/status, never token, query, body or raw errors', () async {
    final logs = <String>[];
    final api = client(MemoryAdapter((_) async => jsonResponse({'message': 'secret-body'}, 401)), logs: logs);
    await expectLater(api.get('/cart', queryParameters: {'private': 'secret-query'}),
      throwsA(isA<ApiException>()));
    final output = logs.join('\n');
    expect(output, contains('GET https://test.invalid/api/v1/cart HTTP=401'));
    expect(output, contains('session=present'));
    expect(output, isNot(contains(tokenFor('test-client'))));
    expect(output, isNot(contains('secret')));
    await expectLater(api.get('/cart/purchase/private-recovery-token'),
      throwsA(isA<ApiException>()));
    expect(logs.join('\n'), isNot(contains('private-recovery-token')));
  });

  for (final isCart in [true, false]) {
    testWidgets('${isCart ? 'cart' : 'reservations'} shows error and read-only retry', (tester) async {
      var failing = true;
      final api = client(MemoryAdapter((_) async => failing
        ? jsonResponse({'message': 'Servicio no disponible'}, 503)
        : jsonResponse(isCart ? emptyCart : [])));
      await tester.pumpWidget(ProviderScope(overrides: [apiClientProvider.overrideWithValue(api)],
        child: MaterialApp(home: isCart ? const CartScreen() : const ReservationsScreen())));
      await tester.pumpAndSettle();
      expect(find.byType(CircularProgressIndicator), findsNothing);
      expect(find.text('Servicio no disponible'), findsWidgets);
      failing = false;
      await tester.tap(find.text(isCart ? 'Consultar de nuevo' : 'Reintentar').first);
      await tester.pumpAndSettle();
      expect(find.text('Servicio no disponible'), findsNothing);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });
  }

  for (final reserve in [false, true]) {
    testWidgets('product button ${reserve ? 'reserves' : 'adds to cart'} actually sends once', (tester) async {
      tester.view.physicalSize = const Size(1080, 1920);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final response = Completer<ResponseBody>();
      final adapter = MemoryAdapter((o) async {
        if (o.method == 'POST') {
          return response.future;
        }
        switch (o.path) {
          case '/catalog/3':
            return jsonResponse({'id': 3, 'name': 'Camisa', 'base_price': 15,
              'variants': [{'id': 7, 'size_name': 'M', 'color_name': 'Azul',
                'available': 8, 'stock': 8}]});
          case '/locations/branches':
            return jsonResponse([{'id': 2, 'name': 'Centro'}]);
          case '/cart':
            return jsonResponse(emptyCart);
          case '/reservations/me':
            return jsonResponse([]);
          default:
            return jsonResponse({'items': []});
        }
      });
      final router = GoRouter(initialLocation: '/product', routes: [
        GoRoute(path: '/product', builder: (_, __) => const ProductDetailScreen(productId: 3)),
        GoRoute(path: '/cart', builder: (_, __) => const Scaffold(body: Text('cart destination'))),
        GoRoute(path: '/reservations', builder: (_, __) => const Scaffold(body: Text('reservations destination'))),
      ]);
      addTearDown(router.dispose);
      await tester.pumpWidget(ProviderScope(overrides: [
        apiClientProvider.overrideWithValue(client(adapter)),
      ], child: MaterialApp.router(routerConfig: router)));
      await tester.pumpAndSettle();
      final button = find.text(reserve ? 'Reservar' : 'Agregar al carrito');
      await tester.tap(button);
      await tester.tap(button); // Two taps before rebuilding must not send twice.
      if (reserve) {
        // The product loading indicators keep animating while the sheet is open.
        await tester.pump(const Duration(seconds: 1));
        expect(adapter.requests.where((o) => o.method == 'POST'), isEmpty);
        await tester.tap(find.byType(DropdownButton<int>));
        await tester.pump(const Duration(seconds: 1));
        await tester.tap(find.text('Centro').last);
        await tester.pump(const Duration(seconds: 1));
        await tester.tap(find.text('Confirmar reserva'));
      }
      await tester.pump(const Duration(seconds: 1));
      final posts = adapter.requests.where((o) => o.method == 'POST').toList();
      expect(posts, hasLength(1));
      expect(posts.single.path, reserve ? '/reservations' : '/cart/items');
      expect(posts.single.data, reserve
        ? {'branch_id': 2, 'items': [{'variant_id': 7, 'quantity': 1}]}
        : {'variant_id': 7, 'quantity': 1});
      expect(find.textContaining('destination'), findsNothing);
      response.complete(jsonResponse(reserve ? reservation : fullCart));
      await tester.pumpAndSettle();
      expect(find.text(reserve ? 'reservations destination' : 'cart destination'), findsOneWidget);
      await tester.pump(const Duration(seconds: 5)); // Dispose the toast timer.
      await tester.pumpAndSettle();
    });
  }
}
