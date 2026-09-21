import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/design/design.dart';
import '../../core/models/models.dart';
import '../../shared/widgets/shared_widgets.dart';
import 'cart_controller.dart';

class CartScreen extends ConsumerStatefulWidget {
  const CartScreen({super.key});

  @override
  ConsumerState<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends ConsumerState<CartScreen> {
  final _couponController = TextEditingController();

  @override
  void dispose() {
    _couponController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(cartControllerProvider);
    final notifier = ref.read(cartControllerProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: Text('Carrito (${state.itemCount})'),
      ),
      body: state.items.isEmpty
          ? const AppEmptyState(
              title: 'Tu carrito está vacío',
              message: 'Explora el catálogo y encuentra tu próximo outfit.',
              icon: Icons.shopping_cart_outlined,
            )
          : RefreshIndicator(
              onRefresh: notifier.load,
              child: ListView(
                padding: const EdgeInsets.all(AppSpacing.x4),
                children: [
                  LayoutBuilder(
                    builder: (context, constraints) {
                      final isWide = constraints.maxWidth >= 900;
                      final items = [
                        for (final item in state.items)
                          _CartItemTile(
                            item: item,
                            onQuantityChanged: (q) =>
                                notifier.updateQuantity(item.variantId, q),
                            onRemove: () => notifier.removeItem(item.variantId),
                          ),
                      ];
                      final summary = Column(
                        children: [
                          CouponCard(
                            controller: _couponController,
                            couponCode: state.couponCode,
                            onApply: () {
                              final code = _couponController.text.trim();
                              if (code.isNotEmpty) notifier.applyCoupon(code);
                            },
                          ),
                          const SizedBox(height: AppSpacing.x4),
                          OrderSummary(
                            subtotal: state.subtotal,
                            shipping: state.shipping,
                            discount: state.discount,
                            total: state.total,
                            onCheckout: () => context.go('/checkout'),
                          ),
                        ],
                      );

                      if (isWide) {
                        return Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(flex: 3, child: Column(children: items)),
                            const SizedBox(width: AppSpacing.x5),
                            Expanded(flex: 2, child: summary),
                          ],
                        );
                      }
                      return Column(
                        children: [
                          ...items,
                          const SizedBox(height: AppSpacing.x4),
                          _couponInline(),
                          const SizedBox(height: AppSpacing.x4),
                          summary,
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),
    );
  }

  Widget _couponInline() {
    final state = ref.watch(cartControllerProvider);
    return Wrap(
      spacing: AppSpacing.x2,
      runSpacing: AppSpacing.x2,
      children: [
        SizedBox(
          width: 220,
          child: AppTextField(
            controller: _couponController,
            hintText: 'Código de cupón',
          ),
        ),
        AppButton(
          label: 'Aplicar',
          variant: AppButtonVariant.outline,
          expand: false,
          onPressed: () {
            final code = _couponController.text.trim();
            if (code.isNotEmpty) {
              ref.read(cartControllerProvider.notifier).applyCoupon(code);
            }
          },
        ),
        if (state.couponCode != null)
          AppBadge(
            label: 'Cupón ${state.couponCode} aplicado',
            variant: AppBadgeVariant.success,
            icon: Icons.redeem,
          ),
      ],
    );
  }
}

class _CartItemTile extends StatelessWidget {
  const _CartItemTile({
    required this.item,
    required this.onQuantityChanged,
    required this.onRemove,
  });

  final CartItem item;
  final ValueChanged<int> onQuantityChanged;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final imageUrl = item.imageUrl;

    return Dismissible(
      key: ValueKey(item.variantId),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onRemove(),
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: AppSpacing.x4),
        decoration: BoxDecoration(
          color: AppColors.error,
          borderRadius: BorderRadius.circular(AppRadius.lg),
        ),
        child: const Icon(Icons.delete_outline, color: Colors.white),
      ),
      child: Container(
        margin: const EdgeInsets.only(bottom: AppSpacing.x3),
        padding: const EdgeInsets.all(AppSpacing.x3),
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(AppRadius.md),
              child: SizedBox(
                width: 76,
                height: 96,
                child: imageUrl != null && imageUrl.isNotEmpty
                    ? CachedNetworkImage(
                        imageUrl: imageUrl,
                        fit: BoxFit.cover,
                        errorWidget: (_, __, ___) => const Icon(
                          Icons.checkroom,
                          color: AppColors.textMuted,
                        ),
                      )
                    : const Icon(
                        Icons.checkroom,
                        color: AppColors.textMuted,
                      ),
              ),
            ),
            const SizedBox(width: AppSpacing.x3),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(
                          item.name,
                          style: theme.textTheme.titleSmall,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      IconButton(
                        onPressed: onRemove,
                        icon: const Icon(Icons.close, size: 18),
                        visualDensity: VisualDensity.compact,
                        tooltip: 'Eliminar',
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    [item.size, item.color].where((e) => e != null).join(' · '),
                    style: theme.textTheme.bodySmall
                        ?.copyWith(color: AppColors.textSecondary),
                  ),
                  const SizedBox(height: AppSpacing.x3),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _MiniStepper(
                        quantity: item.quantity,
                        onChanged: onQuantityChanged,
                      ),
                      Text(
                        _fmt(item.subtotal),
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                          color: AppColors.primaryDark,
                        ),
                      ),
                    ],
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

class _MiniStepper extends StatelessWidget {
  const _MiniStepper({required this.quantity, required this.onChanged});

  final int quantity;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(AppRadius.full),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            onPressed: quantity > 1 ? () => onChanged(quantity - 1) : null,
            icon: const Icon(Icons.remove, size: 16),
            constraints: const BoxConstraints(
              minWidth: 36,
              minHeight: 36,
            ),
            padding: EdgeInsets.zero,
          ),
          SizedBox(
            width: 28,
            child: Text(
              '$quantity',
              textAlign: TextAlign.center,
              style: Theme.of(context)
                  .textTheme
                  .labelLarge
                  ?.copyWith(fontWeight: FontWeight.w700),
            ),
          ),
          IconButton(
            onPressed: quantity < 99 ? () => onChanged(quantity + 1) : null,
            icon: const Icon(Icons.add, size: 16),
            constraints: const BoxConstraints(
              minWidth: 36,
              minHeight: 36,
            ),
            padding: EdgeInsets.zero,
          ),
        ],
      ),
    );
  }
}

class CouponCard extends StatelessWidget {
  const CouponCard({
    super.key,
    required this.controller,
    required this.couponCode,
    required this.onApply,
  });

  final TextEditingController controller;
  final String? couponCode;
  final VoidCallback onApply;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Cupón de descuento',
              style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: AppSpacing.x3),
          if (couponCode != null)
            AppBadge(
              label: 'Cupón $couponCode aplicado',
              variant: AppBadgeVariant.success,
              icon: Icons.redeem,
            )
          else
            Row(
              children: [
                Expanded(
                  child: AppTextField(
                    controller: controller,
                    hintText: 'Ingresa tu código',
                    prefixIcon: Icons.confirmation_number_outlined,
                  ),
                ),
                const SizedBox(width: AppSpacing.x2),
                AppButton(
                  label: 'Aplicar',
                  variant: AppButtonVariant.outline,
                  expand: false,
                  onPressed: onApply,
                ),
              ],
            ),
        ],
      ),
    );
  }
}

class OrderSummary extends StatelessWidget {
  const OrderSummary({
    super.key,
    required this.subtotal,
    required this.shipping,
    required this.discount,
    required this.total,
    required this.onCheckout,
  });

  final double subtotal;
  final double shipping;
  final double discount;
  final double total;
  final VoidCallback onCheckout;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Resumen del pedido',
              style: theme.textTheme.titleSmall),
          const SizedBox(height: AppSpacing.x4),
          _row(theme, 'Subtotal', _fmt(subtotal)),
          const SizedBox(height: AppSpacing.x2),
          _row(
            theme,
            'Envío',
            subtotal >= 999 ? 'GRATIS' : _fmt(shipping),
            color: subtotal >= 999 ? AppColors.success : null,
          ),
          if (discount > 0) ...[
            const SizedBox(height: AppSpacing.x2),
            _row(theme, 'Descuento', '-${_fmt(discount)}',
                color: AppColors.success),
          ],
          const Divider(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Total', style: theme.textTheme.titleMedium),
              Text(
                _fmt(total),
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.primaryDark,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.x4),
          AppButton(
            label: 'Proceder al pago',
            size: AppButtonSize.lg,
            icon: Icons.lock_outline,
            onPressed: onCheckout,
          ),
        ],
      ),
    );
  }

  Widget _row(ThemeData theme, String label, String display,
      {Color? color}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: theme.textTheme.bodyMedium
              ?.copyWith(color: AppColors.textSecondary),
        ),
        Text(
          display,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
      ],
    );
  }
}

String _fmt(double value) {
  final s = value.toStringAsFixed(2);
  return s.endsWith('.00') ? s.substring(0, s.length - 3) : s;
}