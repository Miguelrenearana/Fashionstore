import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/design/design.dart';
import '../../shared/widgets/shared_widgets.dart';
import 'reservation_controller.dart';
import 'reservation_models.dart';

class ReservationsScreen extends ConsumerStatefulWidget {
  const ReservationsScreen({super.key});

  @override
  ConsumerState<ReservationsScreen> createState() => _ReservationsScreenState();
}

class _ReservationsScreenState extends ConsumerState<ReservationsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(reservationControllerProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Mis reservas'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Todas'),
            Tab(text: 'Activas'),
            Tab(text: 'Completadas'),
            Tab(text: 'Canceladas'),
          ],
          labelColor: Colors.white,
          unselectedLabelColor: AppColors.navMuted,
          indicatorColor: AppColors.primary,
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildList(state, null),
          _buildList(state, ReservationStatus.pending),
          _buildList(state, ReservationStatus.pickedUp),
          _buildList(state, ReservationStatus.cancelled),
        ],
      ),
    );
  }

  Widget _buildList(ReservationState state, ReservationStatus? status) {
    final filtered = status == null
        ? state.reservations
        : state.reservations.where((r) => r.status == status).toList();

    if (state.isLoading && filtered.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }
    if (filtered.isEmpty) {
      return const AppEmptyState(
        title: 'No hay reservas aquí',
        message: 'Reserva tus prendas favoritas y recógelas en tienda.',
        icon: Icons.event_available_outlined,
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.x4),
      itemCount: filtered.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.x3),
      itemBuilder: (context, index) {
        final reservation = filtered[index];
        return _ReservationCard(
          reservation: reservation,
          onTap: () =>
              context.go('/reservations/${reservation.id}'),
          onCancel: () async {
            final confirmed = await showDialog<bool>(
              context: context,
              builder: (_) => AlertDialog(
                title: const Text('¿Cancelar reserva?'),
                content: const Text(
                    'Al cancelar, las prendas volverán a estar disponibles.'),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context, false),
                    child: const Text('No'),
                  ),
                  TextButton(
                    onPressed: () => Navigator.pop(context, true),
                    child: const Text('Sí, cancelar'),
                  ),
                ],
              ),
            );
            if (confirmed == true) {
              await ref
                  .read(reservationControllerProvider.notifier)
                  .cancel(reservation.id);
              if (context.mounted) {
                AppToast.show(context,
                    message: 'Reserva cancelada', type: ToastType.success);
              }
            }
          },
        );
      },
    );
  }
}

class _ReservationCard extends StatelessWidget {
  const _ReservationCard({
    required this.reservation,
    required this.onTap,
    required this.onCancel,
  });

  final Reservation reservation;
  final VoidCallback onTap;
  final VoidCallback onCancel;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AppCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.x2,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: AppColors.primaryLight,
                  borderRadius: BorderRadius.circular(AppRadius.full),
                ),
                child: Text(
                  'Reserva #${reservation.id}',
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: AppColors.primaryDark,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              const Spacer(),
              AppBadge(
                label: reservation.status.label,
                variant: reservation.status.badgeVariant,
                showDot: true,
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.x3),
          for (final item in reservation.items.take(3))
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  Icon(item.variantColor != null || item.variantSize != null
                      ? Icons.checkroom
                      : Icons.inventory_2),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodyMedium,
                    ),
                  ),
                  Text(
                    'x${item.quantity}',
                    style: theme.textTheme.bodyMedium
                        ?.copyWith(color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          if (reservation.items.length > 3)
            Text(
              'Y ${reservation.items.length - 3} más…',
              style: theme.textTheme.bodySmall
                  ?.copyWith(color: AppColors.textMuted, fontStyle: FontStyle.italic),
            ),
          const Divider(height: 24),
          Row(
            children: [
              const Icon(
                Icons.storefront_outlined,
                size: 16,
                color: AppColors.textSecondary,
              ),
              const SizedBox(width: 6),
              Text(
                reservation.branch ?? 'Sucursal principal',
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: AppColors.textSecondary),
              ),
              const Spacer(),
              if (reservation.dueCode != null)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.x2,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.successBg,
                    borderRadius: BorderRadius.circular(AppRadius.md),
                  ),
                  child: Text(
                    'Código: ${reservation.dueCode}',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: AppColors.success,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              if (reservation.canCancel)
                TextButton(
                  onPressed: onCancel,
                  style: TextButton.styleFrom(
                    foregroundColor: AppColors.error,
                  ),
                  child: const Text('Cancelar'),
                ),
            ],
          ),
        ],
      ),
    );
  }
}