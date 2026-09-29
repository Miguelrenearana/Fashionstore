import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/models.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';

class CartState {
  const CartState({
    this.items = const [],
    this.isLoading = false,
    this.serverTotal = 0,
    this.error,
  });

  final List<CartItem> items;
  final bool isLoading;

  /// Total que calcula el backend. Es la cifra que se cobra de verdad: usarla
  /// evita mostrar al cliente un importe distinto al de la factura.
  final double serverTotal;
  final String? error;

  double get subtotal => items.fold(0, (sum, item) => sum + item.subtotal);
  double get total => serverTotal > 0 ? serverTotal : subtotal;
  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);
  bool get isEmpty => items.isEmpty;

  CartState copyWith({
    List<CartItem>? items,
    bool? isLoading,
    double? serverTotal,
    String? error,
  }) {
    return CartState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      serverTotal: serverTotal ?? this.serverTotal,
      error: error,
    );
  }
}

class CartController extends StateNotifier<CartState> {
  CartController(this._api) : super(const CartState()) {
    load();
  }

  final ApiClient _api;
  bool _mutating = false;
  int _loadVersion = 0;

  CartState _decode(Map<String, dynamic> res) => CartState(
    items: (res['details'] as List)
      .map((e) => CartItem.fromJson(e as Map<String, dynamic>)).toList(),
    serverTotal: (res['total'] as num).toDouble(),
  );

  Future<void> load() async {
    final version = ++_loadVersion;
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.get('/cart');
      final decoded = _decode(res);
      if (mounted && version == _loadVersion) {
        state = decoded;
      }
    } catch (e) {
      if (mounted && version == _loadVersion) {
        state = state.copyWith(error: e is ApiException ? e.message :
          'No se pudo interpretar la respuesta del carrito.');
      }
    } finally {
      if (mounted && version == _loadVersion) {
        state = state.copyWith(isLoading: false, error: state.error);
      }
    }
  }

  Future<void> addItem(CartItem item) async {
    await _mutate(() => _api.createOnce('/cart/items', data: {
        'variant_id': item.variantId,
        'quantity': item.quantity,
      }, decode: _decode), rethrowError: true);
  }

  Future<void> _mutate(Future<CartState> Function() action,
      {bool rethrowError = false}) async {
    if (_mutating) {
      if (rethrowError) {
        throw ApiException('Hay una actualización del carrito en curso.');
      }
      return;
    }
    _mutating = true;
    ++_loadVersion;
    state = state.copyWith(isLoading: true);
    try {
      final result = await action();
      ++_loadVersion;
      if (mounted) {
        state = result;
      }
    } catch (e) {
      await load(); // Recuperar el estado del servidor sin repetir la escritura.
      if (mounted) {
        state = state.copyWith(error: e is ApiException ? e.message :
          'No se pudo actualizar el carrito. Consulta su estado antes de repetir.');
      }
      if (rethrowError) {
        rethrow;
      }
    } finally {
      _mutating = false;
      if (mounted) {
        state = state.copyWith(isLoading: false, error: state.error);
      }
    }
  }

  Future<void> updateQuantity(int variantId, int quantity) async {
    await _mutate(() async => _decode(await _api.patch('/cart/items/$variantId', data: {
      'variant_id': variantId, 'quantity': quantity,
    })));
  }

  Future<void> removeItem(int variantId) async {
    await _mutate(() async =>
      _decode(await _api.delete('/cart/items/$variantId')));
  }

  Future<void> clear() async {
    state = const CartState();
    try {
      await _api.delete('/cart');
    } catch (_) {}
  }
}

final cartControllerProvider =
    StateNotifierProvider<CartController, CartState>((ref) {
  return CartController(ref.watch(apiClientProvider));
});
