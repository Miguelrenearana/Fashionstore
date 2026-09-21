import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/design/design.dart';
import '../../shared/widgets/shared_widgets.dart';

class Purchase {
  const Purchase({
    required this.id,
    required this.date,
    required this.total,
    required this.itemsCount,
    required this.status,
    this.paymentMethod,
  });

  final int id;
  final DateTime date;
  final double total;
  final int itemsCount;
  final String status;
  final String? paymentMethod;

  factory Purchase.fromJson(Map<String, dynamic> json) {
    return Purchase(
      id: json['id'] as int,
      date: DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.now(),
      total: (json['total'] as num?)?.toDouble() ?? 0,
      itemsCount: json['items_count'] as int? ?? 0,
      status: json['status'] as String? ?? 'completed',
      paymentMethod: json['payment_method'] as String?,
    );
  }
}

class PurchaseHistoryScreen extends ConsumerStatefulWidget {
  const PurchaseHistoryScreen({super.key});

  @override
  ConsumerState<PurchaseHistoryScreen> createState() =>
      _PurchaseHistoryScreenState();
}

class _PurchaseHistoryScreenState extends ConsumerState<PurchaseHistoryScreen> {
  final purchases = <Purchase>[
    Purchase(
      id: 100245,
      date: DateTime(2026, 9, 15),
      total: 1899,
      itemsCount: 3,
      status: 'completed',
      paymentMethod: 'card',
    ),
    Purchase(
      id: 100233,
      date: DateTime(2026, 8, 2),
      total: 849,
      itemsCount: 1,
      status: 'completed',
      paymentMethod: 'card',
    ),
  ];

  String? _filter;

  @override
  Widget build(BuildContext context) {
    final filtered = _filter == null
        ? purchases
        : purchases.where((p) => p.status == _filter).toList();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Historial de compras'),
      ),
      body: filtered.isEmpty
          ? const AppEmptyState(
              title: 'Aún no has realizado compras',
              message: 'Cuando compres, tus comprobantes aparecerán aquí.',
              icon: Icons.receipt_long_outlined,
            )
          : ListView(
              padding: const EdgeInsets.all(AppSpacing.x4),
              children: [
                AppDropdown(
                  items: const [
                    AppDropdownItem(value: 'all', label: 'Todas'),
                    AppDropdownItem(value: 'completed', label: 'Completadas'),
                    AppDropdownItem(value: 'refunded', label: 'Reembolsadas'),
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
  }
}

class _PurchaseCard extends StatelessWidget {
  const _PurchaseCard({required this.purchase});

  final Purchase purchase;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AppCard(
      margin: const EdgeInsets.only(bottom: AppSpacing.x3),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Pedido #${purchase.id}',
                style: theme.textTheme.titleSmall,
              ),
              const Spacer(),
              AppBadge(
                label: _statusLabel(purchase.status),
                variant: purchase.status == 'completed'
                    ? AppBadgeVariant.success
                    : AppBadgeVariant.warning,
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
            ],
          ),
          const Divider(height: 24),
          Row(
            children: [
              Text(
                _fmt(purchase.total),
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.primaryDark,
                ),
              ),
              const Spacer(),
              TextButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.receipt_outlined, size: 18),
                label: const Text('Ver comprobante'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _statusLabel(String status) => switch (status) {
        'completed' => 'Completada',
        'refunded' => 'Reembolsada',
        _ => status,
      };
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
        Text(
          text,
          style: Theme.of(context).textTheme.bodySmall,
        ),
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