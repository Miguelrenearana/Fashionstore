import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/design/design.dart';
import '../../core/di/providers.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/shared_widgets.dart';

/// CU-22: linea del historial, tal como lo devuelve `GET /sales?mine=true`.
class Purchase {
  const Purchase({
    required this.id,
    required this.invoiceNumber,
    required this.date,
    required this.total,
    required this.itemsCount,
    required this.status,
    this.paymentMethod,
    this.details = const [],
  });

  final int id;
  final String invoiceNumber;
  final DateTime date;
  final double total;
  final int itemsCount;
  final String status;
  final String? paymentMethod;
  final List<PurchaseLine> details;

  /// El backend guarda los estados en mayusculas (`COMPLETED`, `REFUNDED`...).
  bool get isCompleted => status == 'COMPLETED';

  /// El comprobante solo existe cuando la venta esta pagada; el backend
  /// responde 404 con "pay first" en ventas pendientes.
  bool get hasReceipt => isCompleted;

  factory Purchase.fromJson(Map<String, dynamic> json) {
    final rawDetails = json['details'] as List<dynamic>? ?? const [];
    return Purchase(
      id: json['id'] as int,
      invoiceNumber: json['invoice_number'] as String? ?? '-',
      date: DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.now(),
      // El campo real es `total_amount`; antes se leia `total` y salia 0.
      total: (json['total_amount'] as num?)?.toDouble() ?? 0,
      itemsCount: json['items_count'] as int? ?? 0,
      status: (json['status'] as String? ?? 'PENDING').toUpperCase(),
      paymentMethod: json['payment_method'] as String?,
      details: rawDetails
          .whereType<Map<String, dynamic>>()
          .map(PurchaseLine.fromJson)
          .toList(),
    );
  }
}

class PurchaseLine {
  const PurchaseLine({
    required this.quantity,
    required this.unitPrice,
    this.garmentName,
    this.sizeName,
    this.colorName,
    this.imageUrl,
  });

  final int quantity;
  final double unitPrice;
  final String? garmentName;
  final String? sizeName;
  final String? colorName;
  final String? imageUrl;

  factory PurchaseLine.fromJson(Map<String, dynamic> json) {
    return PurchaseLine(
      quantity: json['quantity'] as int? ?? 0,
      unitPrice: (json['unit_price'] as num?)?.toDouble() ?? 0,
      garmentName: json['garment_name'] as String?,
      sizeName: json['size_name'] as String?,
      colorName: json['color_name'] as String?,
      imageUrl: json['image_url'] as String?,
    );
  }
}

/// CU-22: historial real. Antes la pantalla traia dos compras inventadas.
final purchaseHistoryProvider =
    FutureProvider.autoDispose<List<Purchase>>((ref) async {
  final res = await ref.read(apiClientProvider).getList(
        '/sales',
        queryParameters: {'mine': 'true'},
      );
  final list = (res)
      .whereType<Map<String, dynamic>>()
      .map(Purchase.fromJson)
      .toList();
  list.sort((a, b) => b.date.compareTo(a.date));
  return list;
});

class PurchaseHistoryScreen extends ConsumerStatefulWidget {
  const PurchaseHistoryScreen({super.key});

  @override
  ConsumerState<PurchaseHistoryScreen> createState() =>
      _PurchaseHistoryScreenState();
}

class _PurchaseHistoryScreenState extends ConsumerState<PurchaseHistoryScreen> {
  String? _filter;

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(purchaseHistoryProvider);
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Historial de compras'),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppEmptyState(
          title: 'No pudimos cargar tu historial',
          message: e.toString(),
          icon: Icons.cloud_off_outlined,
        ),
        data: (purchases) {
          final filtered = _filter == null
              ? purchases
              : purchases.where((p) => p.status == _filter).toList();
          return RefreshIndicator(
            onRefresh: () => ref.refresh(purchaseHistoryProvider.future),
            child: filtered.isEmpty
                ? ListView(
                    children: const [
                      SizedBox(height: 80),
                      AppEmptyState(
                        title: 'Aún no has realizado compras',
                        message: 'Cuando compres, tus comprobantes aparecerán aquí.',
                        icon: Icons.receipt_long_outlined,
                      ),
                    ],
                  )
                : ListView(
                    padding: const EdgeInsets.all(AppSpacing.x4),
                    children: [
                      AppDropdown(
                        items: const [
                          AppDropdownItem(value: 'all', label: 'Todas'),
                          AppDropdownItem(
                            value: 'COMPLETED',
                            label: 'Completadas',
                          ),
                          AppDropdownItem(
                            value: 'PENDING',
                            label: 'Pendientes',
                          ),
                          AppDropdownItem(
                            value: 'REFUNDED',
                            label: 'Reembolsadas',
                          ),
                        ],
                        selected: _filter ?? 'all',
                        onChanged: (v) => setState(
                          () => _filter = v == 'all' ? null : v,
                        ),
                      ),
                      const SizedBox(height: AppSpacing.x4),
                      for (final purchase in filtered)
                        _PurchaseCard(purchase: purchase),
                    ],
                  ),
          );
        },
      ),
    );
  }
}

class _PurchaseCard extends ConsumerWidget {
  const _PurchaseCard({required this.purchase});

  final Purchase purchase;

  Future<void> _openReceipt(BuildContext context, WidgetRef ref) async {
    final api = ref.read(apiClientProvider);
    final messenger = ScaffoldMessenger.of(context);
    try {
      final receipt = await api.get('/sales/${purchase.id}/receipt');
      if (!context.mounted) return;
      await showModalBottomSheet<void>(
        context: context,
        showDragHandle: true,
        builder: (_) => _ReceiptSheet(receipt: receipt, sale: purchase),
      );
    } on ApiException catch (e) {
      // Las ventas pendientes todavia no tienen comprobante emitido.
      messenger.showSnackBar(
        SnackBar(content: Text(e.message)),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    return AppCard(
      margin: const EdgeInsets.only(bottom: AppSpacing.x3),
      onTap: purchase.hasReceipt
          ? () => _openReceipt(context, ref)
          : null,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  purchase.invoiceNumber,
                  style: theme.textTheme.titleSmall,
                ),
              ),
              AppBadge(
                label: _statusLabel(purchase.status),
                variant: _badgeVariant(purchase.status),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.x2),
          Row(
            children: [
              _Meta(
                icon: Icons.calendar_today_outlined,
                text: _fmtDate(purchase.date),
              ),
              const SizedBox(width: AppSpacing.x4),
              _Meta(
                icon: Icons.inventory_2_outlined,
                text: '${purchase.itemsCount} artículos',
              ),
              if (purchase.paymentMethod != null) ...[
                const SizedBox(width: AppSpacing.x4),
                _Meta(
                  icon: purchase.paymentMethod == 'static_qr'
                      ? Icons.qr_code_2
                      : Icons.credit_card,
                  text: _methodLabel(purchase.paymentMethod!),
                ),
              ],
            ],
          ),
          if (purchase.details.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.x3),
            for (final line in purchase.details)
              Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.x2),
                child: Row(
                  children: [
                    const Icon(
                      Icons.checkroom_outlined,
                      size: 16,
                      color: AppColors.textSecondary,
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        '${line.quantity} x ${line.garmentName ?? 'Prenda'}'
                        '${line.sizeName != null ? ' (${line.sizeName})' : ''}',
                        style: theme.textTheme.bodySmall,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
          ],
          const Divider(height: 24),
          Row(
            children: [
              Text(
                'Bs ${_fmt(purchase.total)}',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.primaryDark,
                ),
              ),
              const Spacer(),
              if (purchase.hasReceipt)
                TextButton.icon(
                  onPressed: () => _openReceipt(context, ref),
                  icon: const Icon(Icons.receipt_outlined, size: 18),
                  label: const Text('Ver comprobante'),
                )
              else
                Text(
                  'Pendiente de pago',
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: AppColors.textSecondary),
                ),
            ],
          ),
        ],
      ),
    );
  }

  static AppBadgeVariant _badgeVariant(String status) => switch (status) {
        'COMPLETED' => AppBadgeVariant.success,
        'REFUNDED' => AppBadgeVariant.primary,
        'DECLINED' || 'TIMEOUT' => AppBadgeVariant.error,
        _ => AppBadgeVariant.warning,
      };

  static String _statusLabel(String status) => switch (status) {
        'COMPLETED' => 'Completada',
        'PENDING' => 'Pendiente',
        'REFUNDED' => 'Reembolsada',
        'DECLINED' => 'Rechazada',
        'TIMEOUT' => 'A timeout',
        _ => status,
      };

  static String _methodLabel(String method) => switch (method) {
        'static_qr' => 'Código QR',
        'card' => 'Tarjeta',
        'cash' => 'Efectivo',
        _ => method,
      };
}

class _ReceiptSheet extends StatelessWidget {
  const _ReceiptSheet({required this.receipt, required this.sale});

  final Map<String, dynamic> receipt;
  final Purchase sale;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final rows = <(String, String)>[
      ('Factura', receipt['receipt_number'] as String? ?? sale.invoiceNumber),
      ('Fecha', _fmtDate(sale.date)),
      if (receipt['fiscal_code'] != null)
        ('Codigo fiscal', '${receipt['fiscal_code']}'),
      if (receipt['nit'] != null) ('NIT', '${receipt['nit']}'),
      ('Total', 'Bs ${_fmt(sale.total)}'),
    ];
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.x5,
        0,
        AppSpacing.x5,
        AppSpacing.x5,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Comprobante', style: theme.textTheme.titleMedium),
            const SizedBox(height: AppSpacing.x4),
            for (final (label, value) in rows)
              Padding(
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
              ),
            if (sale.details.isNotEmpty) ...[
              const Divider(height: 28),
              for (final line in sale.details)
                Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.x2),
                  child: Text(
                    '${line.quantity} x ${line.garmentName ?? 'Prenda'} - Bs ${_fmt(line.unitPrice)}',
                    style: theme.textTheme.bodySmall,
                  ),
                ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Meta extends StatelessWidget {
  const _Meta({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: 6),
        Text(text, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

String _fmt(double value) {
  final s = value.toStringAsFixed(2);
  return s.endsWith('.00') ? s.substring(0, s.length - 3) : s;
}

String _fmtDate(DateTime date) {
  return '${date.day} ${_months[date.month - 1]} ${date.year}';
}

const _months = [
  'ene',
  'feb',
  'mar',
  'abr',
  'may',
  'jun',
  'jul',
  'ago',
  'sep',
  'oct',
  'nov',
  'dic',
];
