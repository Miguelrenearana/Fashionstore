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

  Future<void> load() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.get('/cart');
      // El backend llama `details` a las lineas, no `items`.
      final items = (res['details'] as List? ?? const [])
          .map((e) => CartItem.fromJson(e as Map<String, dynamic>))
          .toList();
      state = state.copyWith(
        items: items,
        serverTotal: (res['total'] as num?)?.toDouble() ?? 0,
        isLoading: false,
      );
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    }
  }

  Future<void> addItem(CartItem item) async {
    await _api.post('/cart/items', data: {
      'variant_id': item.variantId,
      'quantity': item.quantity,
    });
    await load();
  }

  Future<void> updateQuantity(int variantId, int quantity) async {
    await _api.patch('/cart/items/$variantId', data: {'quantity': quantity});
    await load();
  }

  Future<void> removeItem(int variantId) async {
    await _api.delete('/cart/items/$variantId');
    await load();
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