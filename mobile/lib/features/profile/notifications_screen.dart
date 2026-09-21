import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/di/providers.dart';
import '../../core/design/design.dart';
import '../../core/models/models.dart';
import '../../shared/widgets/shared_widgets.dart';

/// Mis notificaciones (CU-21): consume `GET /notifications` + `PATCH /{id}/read`.
class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {
  List<NotificationItem> _notifications = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final raw = await ref
          .read(apiClientProvider)
          .getList('/notifications', queryParameters: {'limit': 200});
      final items = raw
          .whereType<Map<String, dynamic>>()
          .map(NotificationItem.fromJson)
          .toList();
      if (mounted) {
        setState(() {
          _notifications = items;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _markRead(NotificationItem n) async {
    if (n.read) return;
    try {
      await ref.read(apiClientProvider).patch('/notifications/${n.id}/read');
      if (mounted) {
        setState(() {
          _notifications = _notifications
              .map((x) => x.id == n.id ? _copyRead(x) : x)
              .toList();
        });
      }
    } catch (_) {
      // Keep it unread on failure; next reload reconciles.
    }
  }

  NotificationItem _copyRead(NotificationItem n) => NotificationItem(
        id: n.id,
        title: n.title,
        body: n.body,
        createdAt: n.createdAt,
        read: true,
        type: n.type,
        deepLink: n.deepLink,
      );

  Future<void> _markAllRead() async {
    for (final n in _notifications.where((x) => !x.read)) {
      await _markRead(n);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Notificaciones'),
        actions: [
          IconButton(
            onPressed: _notifications.isEmpty ? null : _markAllRead,
            icon: const Icon(Icons.done_all),
            tooltip: 'Marcar todas como leídas',
          ),
          IconButton(
            onPressed: _load,
            icon: const Icon(Icons.refresh),
            tooltip: 'Actualizar',
          ),
        ],
      ),
      body: _buildBody(theme),
    );
  }

  Widget _buildBody(ThemeData theme) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    if (_error != null) {
      return AppEmptyState(
        title: 'No se pudieron cargar las notificaciones',
        message: _error!,
        icon: Icons.error_outline,
        actionLabel: 'Reintentar',
        onAction: _load,
      );
    }

    if (_notifications.isEmpty) {
      return const AppEmptyState(
        title: 'Sin notificaciones',
        message: 'Te avisaremos cuando haya novedades.',
        icon: Icons.notifications_none,
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.x4),
      itemCount: _notifications.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.x2),
      itemBuilder: (context, index) {
        final n = _notifications[index];
        return AppCard(
          onTap: () => _markRead(n),
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
    );
  }

  IconData _iconFor(String? type) => switch (type) {
        'RESERVATION' => Icons.event_available_outlined,
        'STOCK' => Icons.inventory_2_outlined,
        'PROMOTION' => Icons.campaign_outlined,
        'password_reset' => Icons.lock_reset,
        'SALE' => Icons.receipt_long_outlined,
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