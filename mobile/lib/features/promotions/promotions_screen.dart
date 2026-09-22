import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/design/design.dart';
import '../../shared/widgets/shared_widgets.dart';
import 'promotion_models.dart';
import 'promotions_controller.dart';

/// CU-11 — Pantalla de promociones activas (cliente).
class PromotionsScreen extends ConsumerStatefulWidget {
  const PromotionsScreen({super.key});

  @override
  ConsumerState<PromotionsScreen> createState() => _PromotionsScreenState();
}

class _PromotionsScreenState extends ConsumerState<PromotionsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() =>
        ref.read(promotionsControllerProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(promotionsControllerProvider);
    final promotions = state.promotions;

    return AppScaffold(
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Promociones (CU-11)'),
      ),
      child: RefreshIndicator(
        onRefresh: () async {
          await ref.read(promotionsControllerProvider.notifier).load();
        },
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(AppSpacing.x4),
          children: [
            if (state.isLoading && promotions.isEmpty)
              ...List.generate(
                4,
                (_) => const Padding(
                  padding: EdgeInsets.only(bottom: AppSpacing.x3),
                  child: AppSkeleton(height: 96),
                ),
              )
            else if (state.error != null)
              AppEmptyState(
                title: 'No se pudieron cargar las promociones',
                message: state.error,
                icon: Icons.error_outline,
                actionLabel: 'Reintentar',
                onAction: () =>
                    ref.read(promotionsControllerProvider.notifier).load(),
              )
            else if (promotions.isEmpty)
              const AppEmptyState(
                title: 'Sin promociones ahora',
                message: 'Vuelve pronto: estamos preparando nuevas ofertas.',
                icon: Icons.local_offer_outlined,
              )
            else
              ...promotions.map(
                (p) => _PromotionTile(
                  promotion: p,
                  onTap: () => _showDetail(p),
                ),
              ),
          ],
        ),
      ),
    );
  }

  void _showDetail(Promotion promo) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        final theme = Theme.of(context);
        return Padding(
          padding: EdgeInsets.only(
            left: AppSpacing.x4,
            right: AppSpacing.x4,
            top: AppSpacing.x4,
            bottom: MediaQuery.of(context).viewInsets.bottom + AppSpacing.x4,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.local_offer_outlined,
                      color: AppColors.primary),
                  const SizedBox(width: AppSpacing.x2),
                  Expanded(
                    child: Text(
                      promo.name,
                      style: theme.textTheme.titleLarge,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.x3),
              Text(
                '${promo.discountPercent.round()}% de descuento',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w700,
                ),
              ),
              if (promo.description != null &&
                  promo.description!.isNotEmpty) ...[
                const SizedBox(height: AppSpacing.x2),
                Text(promo.description!, style: theme.textTheme.bodyMedium),
              ],
              const SizedBox(height: AppSpacing.x4),
              Text(
                'Válido: ${_fmt(promo.startAt)} → ${_fmt(promo.endAt)}',
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: AppColors.textSecondary),
              ),
              const SizedBox(height: AppSpacing.x3),
            ],
          ),
        );
      },
    );
  }

  String _fmt(DateTime d) =>
      '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}';
}

class _PromotionTile extends StatelessWidget {
  const _PromotionTile({required this.promotion, required this.onTap});

  final Promotion promotion;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.x3),
      child: AppCard(
        onTap: onTap,
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.x3,
                vertical: AppSpacing.x2,
              ),
              decoration: BoxDecoration(
                color: AppColors.primaryLight,
                borderRadius: BorderRadius.circular(AppRadius.md),
              ),
              child: Text(
                '${promotion.discountPercent.round()}%',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            const SizedBox(width: AppSpacing.x3),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    promotion.name,
                    style: theme.textTheme.titleMedium,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: AppSpacing.x1),
                  Text(
                    'Hasta ${_fmt(promotion.endAt)}',
                    style: theme.textTheme.bodySmall
                        ?.copyWith(color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: AppColors.textMuted),
          ],
        ),
      ),
    );
  }

  String _fmt(DateTime d) =>
      '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}';
}
