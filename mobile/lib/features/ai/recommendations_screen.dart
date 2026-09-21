import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/design/design.dart';
import '../../core/models/models.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';
import '../../shared/widgets/shared_widgets.dart';
import '../catalog/widgets/product_card.dart';

class RecommendationsState {
  const RecommendationsState({
    this.items = const [],
    this.isLoading = false,
    this.error,
    this.reason,
  });

  final List<ProductRecommendation> items;
  final bool isLoading;
  final String? error;
  final String? reason;

  RecommendationsState copyWith({
    List<ProductRecommendation>? items,
    bool? isLoading,
    String? error,
    String? reason,
  }) {
    return RecommendationsState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      reason: reason ?? this.reason,
    );
  }
}

class RecommendationsController extends StateNotifier<RecommendationsState> {
  RecommendationsController(this._api) : super(const RecommendationsState());

  final ApiClient _api;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.get('/ai/recommendations');
      final items = (res['items'] as List? ?? const [])
          .map((e) => ProductRecommendation.fromJson(e as Map<String, dynamic>))
          .toList();
      state = state.copyWith(
        items: items,
        isLoading: false,
        reason: res['reason'] as String?,
      );
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    }
  }
}

final recommendationsControllerProvider =
    StateNotifierProvider<RecommendationsController, RecommendationsState>(
        (ref) {
  return RecommendationsController(ref.watch(apiClientProvider));
});

class RecommendationsScreen extends ConsumerStatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  ConsumerState<RecommendationsScreen> createState() =>
      _RecommendationsScreenState();
}

class _RecommendationsScreenState
    extends ConsumerState<RecommendationsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(recommendationsControllerProvider.notifier).load(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(recommendationsControllerProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Row(
          children: [
            Icon(Icons.auto_awesome, color: AppColors.primary, size: 22),
            SizedBox(width: 8),
            Text('Recomendados para ti'),
          ],
        ),
      ),
      body: state.error != null && state.items.isEmpty
          ? AppEmptyState(
              title: 'No pudimos cargar recomendaciones',
              message: state.error,
              icon: Icons.cloud_off_outlined,
              actionLabel: 'Reintentar',
              onAction: () => ref
                  .read(recommendationsControllerProvider.notifier)
                  .load(),
            )
          : RefreshIndicator(
              onRefresh: () => ref
                  .read(recommendationsControllerProvider.notifier)
                  .load(),
              child: GridView.builder(
                padding: const EdgeInsets.all(AppSpacing.x4),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: AppSpacing.x4,
                  mainAxisSpacing: AppSpacing.x4,
                  childAspectRatio: 0.66,
                ),
                itemCount: state.isLoading && state.items.isEmpty
                    ? 4
                    : state.items.length,
                itemBuilder: (context, index) {
                  if (state.isLoading && state.items.isEmpty) {
                    return const AppSkeletonCard();
                  }
                  final rec = state.items[index];
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child:
                            ProductCard(product: rec.product, onWishlist: null),
                      ),
                      if (rec.reason != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          '✦ ${rec.reason}',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.labelSmall
                              ?.copyWith(color: AppColors.primary),
                        ),
                      ],
                    ],
                  );
                },
              ),
            ),
    );
  }
}