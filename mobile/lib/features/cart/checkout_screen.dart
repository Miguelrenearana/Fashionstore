import 'package:cached_network_image/cached_network_image.dart';
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

  /// CU-25: el gateway del backend es el que resuelve el cobro. La app no
  /// recoge datos de tarjeta porque nunca se envian al servidor.
  String _method = 'static_qr';
  bool _qrPolling = false;
  String? _paymentStatus;

  OrderResult? _result;

  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  final _cityController = TextEditingController();
  bool _pickup = false;

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    _cityController.dispose();
    super.dispose();
  }

  Future<void> _placeOrder() async {
    setState(() {
      _processing = true;
      _error = null;
    });
    try {
      final res = await ref.read(apiClientProvider).post('/cart/purchase', data: {
        if (!_pickup)
          'shipping_address': {
            'name': _nameController.text.trim(),
            'phone': _phoneController.text.trim(),
            'address': _addressController.text.trim(),
            'city': _cityController.text.trim(),
          },
        'payment_method': _method,
      });
      final result = OrderResult.fromJson(res);
      _result = result;
      _paymentStatus = result.paymentStatus;
      await ref.read(cartControllerProvider.notifier).clear();
      if (!mounted) return;
      setState(() => _step = 3);
      if (result.reference != null) _startPolling(result.reference!);
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _error = e.message;
          _processing = false;
        });
      }
    }
  }

  /// CU-25: consulta el estado real del pago hasta que el gateway lo cierre.
  void _startPolling(String reference) {
    _qrPolling = true;
    _poll(reference);
  }

  Future<void> _poll(String reference) async {
    for (var i = 0; i < 20 && _qrPolling && mounted; i++) {
      await Future<void>.delayed(const Duration(seconds: 3));
      if (!_qrPolling || !mounted) return;
      try {
        final res = await ref
            .read(apiClientProvider)
            .get('/payments/qr/status/$reference');
        final status = res['status'] as String?;
        if (mounted) setState(() => _paymentStatus = status);
        if (status != null &&
            const {'COMPLETED', 'DECLINED', 'REFUNDED', 'TIMEOUT'}.contains(status)) {
          if (mounted) setState(() => _qrPolling = false);
          return;
        }
      } on ApiException {
        // La red puede fallar entre sondeos; se reintenta.
      }
    }
    if (mounted) setState(() => _qrPolling = false);
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
        Text('Método de pago', style: theme.textTheme.titleMedium),
        const SizedBox(height: AppSpacing.x4),
        _methodOption(
          theme,
          value: 'static_qr',
          icon: Icons.qr_code_2,
          title: 'Código QR',
          subtitle: 'Escanea con la app de tu banco. Se confirma al instante.',
          selected: _method == 'static_qr',
        ),
        const SizedBox(height: AppSpacing.x3),
        _methodOption(
          theme,
          value: 'card',
          icon: Icons.credit_card,
          title: 'Tarjeta',
          subtitle: 'Pago simulado por el gateway, sin guardar datos de tarjeta.',
          selected: _method == 'card',
        ),
        const SizedBox(height: AppSpacing.x4),
        AppCard(
          child: Row(
            children: [
              const Icon(Icons.verified_user_outlined, color: AppColors.success),
              const SizedBox(width: AppSpacing.x3),
              Expanded(
                child: Text(
                  'El cobro lo resuelve el gateway de la tienda. Por seguridad, la app no pide ni almacena los datos de tu tarjeta.',
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

  Widget _methodOption(
    ThemeData theme, {
    required String value,
    required IconData icon,
    required String title,
    required String subtitle,
    required bool selected,
  }) {
    return InkWell(
      onTap: () => setState(() => _method = value),
      borderRadius: BorderRadius.circular(AppRadius.md),
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.x4),
        decoration: BoxDecoration(
          color: selected ? AppColors.primaryLight : AppColors.surface,
          borderRadius: BorderRadius.circular(AppRadius.md),
          border: Border.all(
            color: selected ? AppColors.primary : AppColors.border,
            width: selected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(icon, color: selected ? AppColors.primary : AppColors.textSecondary),
            const SizedBox(width: AppSpacing.x3),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: theme.textTheme.titleSmall),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: theme.textTheme.bodySmall
                        ?.copyWith(color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
            if (selected)
              const Icon(Icons.check_circle, color: AppColors.primary),
          ],
        ),
      ),
    );
  }

  Widget _buildSuccess() {
    final theme = Theme.of(context);
    final result = _result;
    final paid = _paymentStatus == 'COMPLETED';
    final failed = const {'DECLINED', 'TIMEOUT'}.contains(_paymentStatus);
    final reference = result?.reference;

    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.x6),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 520),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                width: 96,
                height: 96,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: failed
                      ? AppColors.errorBg
                      : AppColors.successBg,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  failed
                      ? Icons.error_outline
                      : paid
                          ? Icons.check_circle
                          : Icons.schedule,
                  size: 56,
                  color:
                      failed ? AppColors.error : AppColors.success,
                ),
              ),
              const SizedBox(height: AppSpacing.x5),
              Text(
                failed
                    ? 'El pago no se completó'
                    : paid
                        ? '¡Pago confirmado!'
                        : 'Pago pendiente de confirmación',
                textAlign: TextAlign.center,
                style: theme.textTheme.headlineMedium,
              ),
              const SizedBox(height: AppSpacing.x2),
              Text(
                failed
                    ? 'No se realizo el cobro. Puedes reintentar desde el historial.'
                    : paid
                        ? 'Tu compra quedo registrada. Puedes revisarla en tu historial.'
                        : 'Escanea el codigo con tu app bancaria para completar el pago.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium
                    ?.copyWith(color: AppColors.textSecondary),
              ),
              if (result != null) ...[
                const SizedBox(height: AppSpacing.x5),
                AppCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text('Comprobante',
                          style: theme.textTheme.titleSmall),
                      const SizedBox(height: AppSpacing.x3),
                      _kv(theme, 'Factura', result.invoiceNumber),
                      _kv(theme, 'Total', 'Bs ${_fmt(result.total)}'),
                      _kv(theme, 'Estado', _statusLabel(_paymentStatus)),
                      if (reference != null)
                        _kv(theme, 'Referencia', reference),
                    ],
                  ),
                ),
              ],
              if (reference != null && !paid) ...[
                const SizedBox(height: AppSpacing.x4),
                AppCard(
                  child: Column(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(AppRadius.md),
                        child: CachedNetworkImage(
                          imageUrl:
                              '${ref.read(appConfigProvider).apiBaseUrl}/payments/qr/$reference.png',
                          width: 220,
                          height: 220,
                          fit: BoxFit.contain,
                          placeholder: (_, __) => const SizedBox(
                            width: 220,
                            height: 220,
                            child: Center(child: CircularProgressIndicator()),
                          ),
                          errorWidget: (_, __, ___) => const SizedBox(
                            width: 220,
                            height: 220,
                            child: Center(
                              child: Icon(Icons.qr_code_2, size: 180),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: AppSpacing.x3),
                      Text(
                        _qrPolling
                            ? 'Esperando confirmacion del pago...'
                            : 'Escanea con tu app bancaria',
                        style: theme.textTheme.bodySmall
                            ?.copyWith(color: AppColors.textSecondary),
                      ),
                    ],
                  ),
                ),
              ],
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
      ),
    );
  }

  Widget _kv(ThemeData theme, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.x2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: theme.textTheme.bodyMedium
                ?.copyWith(color: AppColors.textSecondary),
          ),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: theme.textTheme.bodyMedium
                  ?.copyWith(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  static String _statusLabel(String? status) {
    switch (status) {
      case 'COMPLETED':
        return 'Pagado';
      case 'DECLINED':
        return 'Rechazado';
      case 'REFUNDED':
        return 'Reembolsado';
      case 'TIMEOUT':
        return 'A timeout';
      case 'PENDING':
        return 'Pendiente';
      default:
        return status ?? 'Desconocido';
    }
  }
}

/// Resultado de `POST /cart/purchase` (CU-21 / CU-25).
class OrderResult {
  const OrderResult({
    required this.invoiceNumber,
    required this.total,
    required this.saleStatus,
    required this.paymentStatus,
    this.reference,
  });

  final String invoiceNumber;
  final double total;
  final String saleStatus;
  final String paymentStatus;
  final String? reference;

  factory OrderResult.fromJson(Map<String, dynamic> json) {
    final sale = json['sale'] as Map<String, dynamic>? ?? const {};
    final payment = json['payment'] as Map<String, dynamic>? ?? const {};
    return OrderResult(
      invoiceNumber: sale['invoice_number'] as String? ?? '-',
      total: (sale['total_amount'] as num?)?.toDouble() ?? 0,
      saleStatus: sale['status'] as String? ?? 'PENDING',
      paymentStatus: payment['status'] as String? ?? 'PENDING',
      reference: payment['gateway_reference'] as String?,
    );
  }
}

String _fmt(double value) {
  final s = value.toStringAsFixed(2);
  return s.endsWith('.00') ? s.substring(0, s.length - 3) : s;
}