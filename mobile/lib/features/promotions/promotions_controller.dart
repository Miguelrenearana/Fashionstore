import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/di/providers.dart';
import '../../core/network/api_client.dart';
import 'promotion_models.dart';

class PromotionsState {
  const PromotionsState({
    this.promotions = const [],
    this.isLoading = false,
    this.error,
  });

  final List<Promotion> promotions;
  final bool isLoading;
  final String? error;

  PromotionsState copyWith({
    List<Promotion>? promotions,
    bool? isLoading,
    String? error,
  }) {
    return PromotionsState(
      promotions: promotions ?? this.promotions,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class PromotionsController extends StateNotifier<PromotionsState> {
  PromotionsController(this._api) : super(const PromotionsState());

  final ApiClient _api;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.get('/promotions', queryParameters: {
        'active_only': true,
        'page': 1,
        'size': 100,
      });
      final items = ((res['items'] as List?) ?? const [])
          .map((e) => Promotion.fromJson(e as Map<String, dynamic>))
          .toList();
      state = state.copyWith(promotions: items, isLoading: false);
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    }
  }
}

final promotionsControllerProvider =
    StateNotifierProvider<PromotionsController, PromotionsState>((ref) {
  return PromotionsController(ref.watch(apiClientProvider));
});
