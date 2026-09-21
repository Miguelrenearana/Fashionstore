import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/design/design.dart';
import '../../core/models/models.dart';
import '../../shared/widgets/shared_widgets.dart';

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final notifications = <NotificationItem>[
      NotificationItem(
        id: 1,
        title: 'Tu reserva está lista',
        body: 'La prenda que reservaste ya está lista para recoger en la sucursal.',
        createdAt: DateTime(2026, 9, 20, 14, 30),
        type: 'reservation',
      ),
      NotificationItem(
        id: 2,
        title: 'Nuevo en la colección',
        body: 'Descubre la nueva colección de otoño en FashionStore.',
        createdAt: DateTime(2026, 9, 18, 10, 0),
        type: 'marketing',
      ),
    ];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Notificaciones'),
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.done_all),
            tooltip: 'Marcar todas como leídas',
          ),
        ],
      ),
      body: notifications.isEmpty
          ? const AppEmptyState(
              title: 'Sin notificaciones',
              message: 'Te avisaremos cuando haya novedades.',
              icon: Icons.notifications_none,
            )
          : ListView.separated(
              padding: const EdgeInsets.all(AppSpacing.x4),
              itemCount: notifications.length,
              separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.x2),
              itemBuilder: (context, index) {
                final n = notifications[index];
                return AppCard(
                  onTap: () {},
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 44,
                        height: 44,
                        decoration: const BoxDecoration(
                          color: AppColors.primaryLight,
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          _iconFor(n.type),
                          color: AppColors.primary,
                          size: 22,
                        ),
                      ),
                      const SizedBox(width: AppSpacing.x3),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              n.title,
                              style: theme.textTheme.titleSmall?.copyWith(
                                fontWeight: n.read ? FontWeight.w500 : FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              n.body,
                              style: theme.textTheme.bodySmall
                                  ?.copyWith(color: AppColors.textSecondary),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              _timeAgo(n.createdAt),
                              style: theme.textTheme.labelSmall
                                  ?.copyWith(color: AppColors.textMuted),
                            ),
                          ],
                        ),
                      ),
                      if (!n.read)
                        Container(
                          width: 8,
                          height: 8,
                          margin: const EdgeInsets.only(top: 6),
                          decoration: const BoxDecoration(
                            color: AppColors.primary,
                            shape: BoxShape.circle,
                          ),
                        ),
                    ],
                  ),
                );
              },
            ),
    );
  }

  IconData _iconFor(String? type) => switch (type) {
        'reservation' => Icons.event_available_outlined,
        'marketing' => Icons.campaign_outlined,
        _ => Icons.notifications_none,
      };

  String _timeAgo(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inMinutes < 1) return 'Ahora';
    if (diff.inMinutes < 60) return 'Hace ${diff.inMinutes} min';
    if (diff.inHours < 24) return 'Hace ${diff.inHours} h';
    return 'Hace ${diff.inDays} d';
  }
}