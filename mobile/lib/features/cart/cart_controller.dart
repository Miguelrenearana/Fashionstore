import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/models.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';

class CartState {
  const CartState({
    this.items = const [],
    this.isLoading = false,
    this.couponCode,
    this.discount = 0,
    this.error,
  });

  final List<CartItem> items;
  final bool isLoading;
  final String? couponCode;
  final double discount;
  final String? error;

  double get subtotal => items.fold(0, (sum, item) => sum + item.subtotal);
  double get shipping => subtotal >= 999 || items.isEmpty ? 0 : 99;
  double get total => (subtotal - discount + shipping).clamp(0, double.infinity);
  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);

  CartState copyWith({
    List<CartItem>? items,
    bool? isLoading,
    String? couponCode,
    double? discount,
    String? error,
  }) {
    return CartState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      couponCode: couponCode ?? this.couponCode,
      discount: discount ?? this.discount,
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
      final items = (res['items'] as List? ?? const [])
          .map((e) => CartItem.fromJson(e as Map<String, dynamic>))
          .toList();
      state = state.copyWith(items: items, isLoading: false);
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

  Future<void> applyCoupon(String code) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.post('/cart/coupon', data: {'code': code});
      state = state.copyWith(
        couponCode: code,
        discount: (res['discount'] as num?)?.toDouble() ?? 0,
        isLoading: false,
      );
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    }
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