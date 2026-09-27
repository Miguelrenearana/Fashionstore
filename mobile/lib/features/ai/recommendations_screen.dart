import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

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
      // `getList` porque el endpoint devuelve una lista JSON de primer nivel;
      // `get` hacia `res.data as Map` y reventaba con una lista.
      final data = await _api.getList(
        '/ai/recommendations',
        queryParameters: {'source': 'trending', 'limit': 10},
      );
      final items = data
          .whereType<Map<String, dynamic>>()
          .map(ProductRecommendation.fromJson)
          .toList();
      state = state.copyWith(items: items, isLoading: false);
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    } on Object catch (e) {
      state = state.copyWith(isLoading: false, error: 'Error: $e');
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
        actions: [
          IconButton(
            onPressed: () => context.go('/ai/chat'),
            icon: const Icon(Icons.chat_bubble_outline),
            tooltip: 'Asistente IA',
          ),
        ],
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
                      const SizedBox(height: 4),
                      // La recomendacion viene por variante concreta, asi que se
                      // informa talla y color: antes solo se mostraba el nombre.
                      if (rec.sizeName != null || rec.colorName != null)
                        Text(
                          [
                            if (rec.sizeName != null) 'Talla ${rec.sizeName}',
                            if (rec.colorName != null) rec.colorName!,
                          ].join(' - '),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.labelSmall
                              ?.copyWith(color: AppColors.textSecondary),
                        ),
                      if (rec.reason != null) ...[
                        const SizedBox(height: 2),
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