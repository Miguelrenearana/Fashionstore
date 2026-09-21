import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/design/design.dart';
import '../../../core/models/catalog.dart';
import '../../../shared/widgets/shared_widgets.dart';

class ProductCard extends StatelessWidget {
  const ProductCard({
    super.key,
    required this.product,
    this.onWishlist,
    this.isWishlisted = false,
  });

  final Product product;
  final VoidCallback? onWishlist;
  final bool isWishlisted;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final imageUrl = product.primaryImage;
    final hasImage = imageUrl.isNotEmpty;

    return GestureDetector(
      onTap: () => context.go('/catalog/${product.id}'),
      child: Container(
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(
            color: theme.brightness == Brightness.dark
                ? AppColors.darkBorder
                : AppColors.border,
          ),
          boxShadow: AppShadows.sm,
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                AspectRatio(
                  aspectRatio: 1,
                  child: hasImage
                      ? CachedNetworkImage(
                          imageUrl: imageUrl,
                          fit: BoxFit.cover,
                          placeholder: (_, __) => const AppSkeleton(
                            width: double.infinity,
                            height: double.infinity,
                          ),
                          errorWidget: (_, __, ___) => const _ImageFallback(),
                        )
                      : const _ImageFallback(),
                ),
                if (product.hasDiscount)
                  Positioned(
                    top: 8,
                    left: 8,
                    child: AppBadge(
                      label: '-${product.discount.round()}%',
                      variant: AppBadgeVariant.error,
                      size: AppBadgeSize.sm,
                    ),
                  ),
                if (product.isNew)
                  Positioned(
                    top: 8,
                    left: product.hasDiscount ? 62 : 8,
                    child: const AppBadge(
                      label: 'NUEVO',
                      variant: AppBadgeVariant.primary,
                      size: AppBadgeSize.sm,
                    ),
                  ),
                Positioned(
                  top: 4,
                  right: 4,
                  child: IconButton(
                    onPressed: onWishlist,
                    icon: Icon(
                      isWishlisted
                          ? Icons.favorite
                          : Icons.favorite_border,
                      color: isWishlisted ? AppColors.error : Colors.white,
                      size: 20,
                    ),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.black.withValues(alpha: 0.25),
                    ),
                    tooltip: isWishlisted
                        ? 'Quitar de favoritos'
                        : 'Agregar a favoritos',
                  ),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.all(AppSpacing.x3),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.category ?? 'Ropa',
                    style: theme.textTheme.labelSmall
                        ?.copyWith(color: AppColors.textMuted),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    product.name,
                    style: theme.textTheme.titleSmall,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: AppSpacing.x2),
                  CurrentPriceText(product: product),
                  if (product.rating > 0)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.star,
                            size: 14,
                            color: AppColors.warning,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            '${product.rating.toStringAsFixed(1)} (${product.reviewCount})',
                            style: theme.textTheme.labelSmall
                                ?.copyWith(color: AppColors.textSecondary),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ImageFallback extends StatelessWidget {
  const _ImageFallback();

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.surfaceAlt,
      child: const Center(
        child: Icon(
          Icons.checkroom,
          size: 48,
          color: AppColors.textMuted,
        ),
      ),
    );
  }
}