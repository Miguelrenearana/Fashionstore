import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/design/design.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';
import '../../shared/widgets/shared_widgets.dart';
import 'cart_controller.dart';

class CheckoutScreen extends ConsumerStatefulWidget {
  const CheckoutScreen({super.key});

  @override
  ConsumerState<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends ConsumerState<CheckoutScreen> {
  int _step = 0;
  bool _processing = false;
  String? _error;

  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  final _cityController = TextEditingController();
  bool _pickup = false;

  final _cardNumberController = TextEditingController();
  final _cardNameController = TextEditingController();
  final _cardExpiryController = TextEditingController();
  final _cardCvcController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    _cityController.dispose();
    _cardNumberController.dispose();
    _cardNameController.dispose();
    _cardExpiryController.dispose();
    _cardCvcController.dispose();
    super.dispose();
  }

  Future<void> _placeOrder() async {
    setState(() {
      _processing = true;
      _error = null;
    });
    try {
      await ref.read(apiClientProvider).post('/cart/purchase', data: {
        'shipping_address': _pickup
            ? null
            : {
                'name': _nameController.text.trim(),
                'phone': _phoneController.text.trim(),
                'address': _addressController.text.trim(),
                'city': _cityController.text.trim(),
              },
        'payment_method': 'card',
      });
      await ref.read(cartControllerProvider.notifier).clear();
      if (mounted) setState(() => _step = 3);
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _error = e.message;
          _processing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(cartControllerProvider);
    final theme = Theme.of(context);

    if (state.items.isEmpty && _step != 3) {
      return Scaffold(
        appBar: AppBar(title: const Text('Checkout')),
        body: const AppEmptyState(
          title: 'Tu carrito está vacío',
          icon: Icons.shopping_cart_outlined,
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Checkout'),
        leading: _step > 0 && _step < 3
            ? IconButton(
                onPressed: () => setState(() => _step--),
                icon: const Icon(Icons.arrow_back),
              )
            : const BackButton(),
      ),
      body: _step == 3
          ? _buildSuccess()
          : Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(AppSpacing.x5),
                  child: AppStepper(
                    steps: const [
                      AppStep(label: 'Carrito', icon: Icons.shopping_cart_outlined),
                      AppStep(label: 'Envío', icon: Icons.local_shipping_outlined),
                      AppStep(label: 'Pago', icon: Icons.credit_card),
                    ],
                    currentStep: _step,
                    onStepTap: (i) {
                      if (i < _step) setState(() => _step = i);
                    },
                  ),
                ),
                const Divider(height: 1, color: AppColors.border),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(AppSpacing.x5),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 640),
                      child: switch (_step) {
                        0 => _buildCartStep(state, theme),
                        1 => _buildShippingStep(theme),
                        _ => _buildPaymentStep(theme),
                      },
                    ),
                  ),
                ),
                SafeArea(
                  top: false,
                  child: Container(
                    padding: const EdgeInsets.all(AppSpacing.x4),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surface,
                      boxShadow: AppShadows.md,
                    ),
                    child: AppButton(
                      label: switch (_step) {
                        0 => 'Continuar a envío',
                        1 => 'Continuar a pago',
                        _ => 'Pagar ${_fmt(state.total)}',
                      },
                      loading: _processing,
                      size: AppButtonSize.lg,
                      icon: _step == 2 ? Icons.lock_outline : Icons.arrow_forward,
                      onPressed: () {
                        if (_step == 0) {
                          setState(() => _step = 1);
                        } else if (_step == 1) {
                          setState(() => _step = 2);
                        } else {
                          _placeOrder();
                        }
                      },
                    ),
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildCartStep(CartState state, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final item in state.items)
          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: Container(
              width: 56,
              height: 72,
              decoration: BoxDecoration(
                color: AppColors.surfaceAlt,
                borderRadius: BorderRadius.circular(AppRadius.md),
              ),
              child: const Icon(Icons.checkroom, color: AppColors.textMuted),
            ),
            title: Text(item.name, maxLines: 2, overflow: TextOverflow.ellipsis),
            subtitle: Text(
              '${item.size ?? ''} ${item.color ?? ''} · x${item.quantity}',
              style: theme.textTheme.bodySmall,
            ),
            trailing: Text(
              _fmt(item.subtotal),
              style: theme.textTheme.titleSmall
                  ?.copyWith(fontWeight: FontWeight.w700),
            ),
          ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.x3),
            child: AppBadge(
              label: _error!,
              variant: AppBadgeVariant.error,
              icon: Icons.error_outline,
            ),
          ),
      ],
    );
  }

  Widget _buildShippingStep(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Datos de envío', style: theme.textTheme.titleMedium),
        const SizedBox(height: AppSpacing.x4),
        SwitchListTile(
          value: _pickup,
          onChanged: (v) => setState(() => _pickup = v),
          contentPadding: EdgeInsets.zero,
          title: const Text('Recoger en tienda'),
          subtitle: const Text(
            'Sin costo de envío · Nota: validado al llegar',
            style: TextStyle(fontSize: 13),
          ),
        ),
        const SizedBox(height: AppSpacing.x3),
        if (!_pickup) ...[
          AppTextField(
            controller: _nameController,
            label: 'Nombre del destinatario',
            prefixIcon: Icons.person_outline,
          ),
          const SizedBox(height: AppSpacing.x3),
          AppTextField(
            controller: _phoneController,
            label: 'Teléfono',
            prefixIcon: Icons.phone_outlined,
            keyboardType: TextInputType.phone,
          ),
          const SizedBox(height: AppSpacing.x3),
          AppTextField(
            controller: _addressController,
            label: 'Dirección',
            prefixIcon: Icons.location_on_outlined,
          ),
          const SizedBox(height: AppSpacing.x3),
          AppTextField(
            controller: _cityController,
            label: 'Ciudad',
            prefixIcon: Icons.location_city_outlined,
          ),
        ] else
          AppCard(
            child: Row(
              children: [
                const Icon(Icons.storefront, color: AppColors.primary),
                const SizedBox(width: AppSpacing.x3),
                Expanded(
                  child: Text(
                    'Elige la sucursal al confirmar la compra. ',
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildPaymentStep(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Información de pago', style: theme.textTheme.titleMedium),
        const SizedBox(height: AppSpacing.x4),
        AppTextField(
          controller: _cardNumberController,
          label: 'Número de tarjeta',
          hintText: '1234 5678 9012 3456',
          prefixIcon: Icons.credit_card,
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: AppSpacing.x3),
        AppTextField(
          controller: _cardNameController,
          label: 'Nombre en la tarjeta',
          prefixIcon: Icons.person_outline,
        ),
        const SizedBox(height: AppSpacing.x3),
        Row(
          children: [
            Expanded(
              child: AppTextField(
                controller: _cardExpiryController,
                label: 'Vencimiento',
                hintText: 'MM/AA',
                prefixIcon: Icons.calendar_today_outlined,
              ),
            ),
            const SizedBox(width: AppSpacing.x3),
            Expanded(
              child: AppTextField(
                controller: _cardCvcController,
                label: 'CVC',
                hintText: '123',
                prefixIcon: Icons.lock_outline,
                obscureText: true,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.x4),
        AppCard(
          child: Row(
            children: [
              const Icon(Icons.verified_user_outlined, color: AppColors.success),
              const SizedBox(width: AppSpacing.x3),
              Expanded(
                child: Text(
                  'Tus datos están protegidos con cifrado. Este pago es simulado para fines de demostración.',
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: AppColors.textSecondary),
                ),
              ),
            ],
          ),
        ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(top: AppSpacing.x3),
            child: AppBadge(
              label: _error!,
              variant: AppBadgeVariant.error,
              icon: Icons.error_outline,
            ),
          ),
      ],
    );
  }

  Widget _buildSuccess() {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.x6),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 96,
              height: 96,
              decoration: const BoxDecoration(
                color: AppColors.successBg,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check_circle,
                size: 56,
                color: AppColors.success,
              ),
            ),
            const SizedBox(height: AppSpacing.x5),
            Text(
              '¡Compra confirmada!',
              style: theme.textTheme.headlineMedium,
            ),
            const SizedBox(height: AppSpacing.x2),
            Text(
              'Recibirás tu comprobante por correo. Puedes darle seguimiento desde tu historial de compras.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium
                  ?.copyWith(color: AppColors.textSecondary),
            ),
            const SizedBox(height: AppSpacing.x6),
            AppButton(
              label: 'Ver historial de compras',
              size: AppButtonSize.lg,
              onPressed: () => context.go('/profile/orders'),
            ),
            const SizedBox(height: AppSpacing.x2),
            TextButton(
              onPressed: () => context.go('/catalog'),
              child: const Text('Seguir comprando'),
            ),
          ],
        ),
      ),
    );
  }
}

String _fmt(double value) {
  final s = value.toStringAsFixed(2);
  return s.endsWith('.00') ? s.substring(0, s.length - 3) : s;
}