import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/design/design.dart';
import '../../shared/widgets/shared_widgets.dart';
import 'reservation_controller.dart';
import 'reservation_models.dart';

class ReservationDetailScreen extends ConsumerStatefulWidget {
  const ReservationDetailScreen({super.key, required this.reservationId});

  final int reservationId;

  @override
  ConsumerState<ReservationDetailScreen> createState() =>
      _ReservationDetailScreenState();
}

class _ReservationDetailScreenState
    extends ConsumerState<ReservationDetailScreen> {
  Reservation? _reservation;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final existing = ref.read(reservationControllerProvider).reservations
        .where((r) => r.id == widget.reservationId)
        .firstOrNull;
    if (existing != null) {
      setState(() {
        _reservation = existing;
        _loading = false;
      });
      return;
    }
    final detail = await ref
        .read(reservationControllerProvider.notifier)
        .detail(widget.reservationId);
    if (!mounted) return;
    setState(() {
      _reservation = detail;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Detalle de reserva'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _reservation == null
              ? const AppEmptyState(
                  title: 'Reserva no encontrada',
                  icon: Icons.event_busy_outlined,
                )
              : _buildDetail(_reservation!, theme),
    );
  }

  Widget _buildDetail(Reservation reservation, ThemeData theme) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.x4),
      children: [
        AppCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    reservation.status.icon,
                    color: AppColors.primary,
                    size: 28,
                  ),
                  const SizedBox(width: AppSpacing.x3),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Reserva #${reservation.id}',
                          style: theme.textTheme.titleMedium,
                        ),
                        Text(
                          'Creada el ${_fmtDate(reservation.createdAt)}',
                          style: theme.textTheme.bodySmall
                              ?.copyWith(color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                  AppBadge(
                    label: reservation.status.label,
                    variant: reservation.status.badgeVariant,
                    showDot: true,
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.x4),
        Text('Prendas', style: theme.textTheme.titleMedium),
        const SizedBox(height: AppSpacing.x3),
        AppCard(
          child: Column(
            children: [
              for (final item in reservation.items)
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Container(
                    width: 48,
                    height: 60,
                    decoration: BoxDecoration(
                      color: AppColors.surfaceAlt,
                      borderRadius: BorderRadius.circular(AppRadius.md),
                    ),
                    child: const Icon(
                      Icons.checkroom,
                      color: AppColors.textMuted,
                    ),
                  ),
                  title: Text(item.name),
                  subtitle: Text(
                    [item.variantSize, item.variantColor]
                        .where((e) => e != null)
                        .join(' · '),
                    style: theme.textTheme.bodySmall,
                  ),
                  isThreeLine: false,
                  trailing: Text(
                    'x${item.quantity} · ${_fmt(item.price * item.quantity)}',
                    style: theme.textTheme.bodyMedium
                        ?.copyWith(fontWeight: FontWeight.w600),
                  ),
                ),
              const Divider(),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Total', style: theme.textTheme.titleSmall),
                  Text(
                    _fmt(reservation.total),
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: AppColors.primaryDark,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.x4),
        if (reservation.dueCode != null)
          AppCard(
            color: AppColors.successBg,
            child: Row(
              children: [
                const Icon(Icons.qr_code, color: AppColors.success, size: 40),
                const SizedBox(width: AppSpacing.x3),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Código de recogida',
                      style: theme.textTheme.labelMedium
                          ?.copyWith(color: AppColors.success),
                    ),
                    Text(
                      reservation.dueCode!,
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: AppColors.success,
                        letterSpacing: 2,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        const SizedBox(height: AppSpacing.x4),
        _buildTimeline(reservation, theme),
        const SizedBox(height: AppSpacing.x4),
        if (reservation.canCancel)
          AppButton(
            label: 'Cancelar reserva',
            variant: AppButtonVariant.danger,
            icon: Icons.cancel_outlined,
            onPressed: () async {
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (_) => AlertDialog(
                  title: const Text('¿Cancelar reserva?'),
                  content: const Text('Esta acción no se puede deshacer.'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: const Text('No'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: const Text('Sí'),
                    ),
                  ],
                ),
              );
              if (confirmed == true && mounted) {
                await ref
                    .read(reservationControllerProvider.notifier)
                    .cancel(reservation.id);
                if (mounted) {
                  Navigator.maybePop(context);
                  AppToast.show(context,
                      message: 'Reserva cancelada', type: ToastType.success);
                }
              }
            },
          ),
      ],
    );
  }

  Widget _buildTimeline(Reservation reservation, ThemeData theme) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Estado', style: theme.textTheme.titleMedium),
          const SizedBox(height: AppSpacing.x4),
          const _TimelineRow(
            icon: Icons.event_available,
            label: 'Reserva creada',
            done: true,
          ),
          _TimelineRow(
            icon: Icons.verified_user,
            label: 'Prendas preparadas',
            done: reservation.status.index >= ReservationStatus.ready.index,
          ),
          _TimelineRow(
            icon: Icons.shopping_bag,
            label: 'Recogida en tienda',
            done: reservation.status == ReservationStatus.pickedUp,
          ),
        ],
      ),
    );
  }
}

class _TimelineRow extends StatelessWidget {
  const _TimelineRow({
    required this.icon,
    required this.label,
    required this.done,
  });

  final IconData icon;
  final String label;
  final bool done;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = done ? AppColors.success : AppColors.textMuted;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(width: AppSpacing.x3),
          Text(
            label,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: done ? AppColors.success : AppColors.textSecondary,
              fontWeight: done ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
          const Spacer(),
          Icon(
            done ? Icons.check_circle : Icons.radio_button_unchecked,
            color: color,
            size: 18,
          ),
        ],
      ),
    );
  }
}

extension _FirstOrNull on Iterable<Reservation> {
  Reservation? get firstOrNull {
    final it = iterator;
    return it.moveNext() ? it.current : null;
  }
}

String _fmt(double value) {
  final s = value.toStringAsFixed(2);
  return s.endsWith('.00') ? s.substring(0, s.length - 3) : s;
}

String _fmtDate(DateTime date) {
  return '${date.day}/${date.month}/${date.year}';
}