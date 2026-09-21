import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/design/design.dart';
import '../../core/models/models.dart';
import '../../shared/widgets/shared_widgets.dart';
import '../auth/auth_controller.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _nameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(authControllerProvider);
    final user = state.user;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Text('Mi perfil'),
      ),
      body: user == null
          ? AppEmptyState(
              title: 'Inicia sesión',
              message: 'Accede a tu perfil, reservas y compras.',
              icon: Icons.person_outline,
              actionLabel: 'Iniciar sesión',
              onAction: () => context.go('/auth/login'),
            )
          : Column(
              children: [
                _ProfileHeader(user: user),
                TabBar(
                  controller: _tabController,
                  labelColor: AppColors.primaryDark,
                  unselectedLabelColor: AppColors.textSecondary,
                  indicatorColor: AppColors.primary,
                  dividerColor: Colors.transparent,
                  tabs: const [
                    Tab(text: 'Datos'),
                    Tab(text: 'Favoritos'),
                    Tab(text: 'Cuenta'),
                  ],
                ),
                Expanded(
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _PersonalDataTab(
                        nameController: _nameController,
                        phoneController: _phoneController,
                        saving: _saving,
                        onSave: _saveProfile,
                      ),
                      _FavoritesTab(),
                      _AccountTab(onLogout: _logout),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  Future<void> _saveProfile() async {
    setState(() => _saving = true);
    await ref.read(authControllerProvider.notifier).updateProfile(
          User(
            id: ref.read(authControllerProvider).user!.id,
            email: ref.read(authControllerProvider).user!.email,
            fullName: _nameController.text.trim(),
            phone: _phoneController.text.trim(),
          ),
        );
    if (mounted) {
      setState(() => _saving = false);
      AppToast.show(context,
          message: 'Perfil actualizado', type: ToastType.success);
    }
  }

  Future<void> _logout() async {
    await ref.read(authControllerProvider.notifier).logout();
    if (mounted) context.go('/catalog');
  }
}

class _ProfileHeader extends StatelessWidget {
  const _ProfileHeader({required this.user});

  final User user;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      color: AppColors.navBg,
      padding: const EdgeInsets.all(AppSpacing.x5),
      child: Row(
        children: [
          AppAvatar(
            imageUrl: user.avatarUrl,
            initials: _initials(user.fullName),
            size: 64,
          ),
          const SizedBox(width: AppSpacing.x4),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  user.fullName.isEmpty ? user.email : user.fullName,
                  style: theme.textTheme.titleLarge
                      ?.copyWith(color: Colors.white),
                ),
                Text(
                  user.email,
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: AppColors.navMuted),
                ),
                if (user.points > 0)
                  Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: AppBadge(
                      label: '${user.points} puntos',
                      variant: AppBadgeVariant.primary,
                      icon: Icons.stars,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _initials(String name) {
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.isEmpty || parts.first.isEmpty) return 'FS';
    if (parts.length == 1) return parts.first.substring(0, 1).toUpperCase();
    return (parts.first[0] + parts.last[0]).toUpperCase();
  }
}

class _PersonalDataTab extends StatelessWidget {
  const _PersonalDataTab({
    required this.nameController,
    required this.phoneController,
    required this.saving,
    required this.onSave,
  });

  final TextEditingController nameController;
  final TextEditingController phoneController;
  final bool saving;
  final VoidCallback onSave;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.x5),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            AppTextField(
              controller: nameController,
              label: 'Nombre completo',
              prefixIcon: Icons.person_outline,
            ),
            const SizedBox(height: AppSpacing.x3),
            AppTextField(
              controller: phoneController,
              label: 'Teléfono',
              prefixIcon: Icons.phone_outlined,
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: AppSpacing.x4),
            AppButton(
              label: 'Guardar cambios',
              loading: saving,
              onPressed: onSave,
            ),
            const SizedBox(height: AppSpacing.x5),
            Text('Direcciones', style: theme.textTheme.titleMedium),
            const SizedBox(height: AppSpacing.x3),
            AppCard(
              child: Row(
                children: [
                  const Icon(Icons.location_on_outlined,
                      color: AppColors.primary),
                  const SizedBox(width: AppSpacing.x3),
                  Expanded(
                    child: Text(
                      'No has agregado direcciones todavía.',
                      style: theme.textTheme.bodyMedium,
                    ),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.add_circle_outline),
                    tooltip: 'Agregar dirección',
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

class _FavoritesTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const AppEmptyState(
      title: 'Sin favoritos aún',
      message: 'Guarda tus prendas favoritas para encontrarlas fácilmente.',
      icon: Icons.favorite_border,
    );
  }
}

class _AccountTab extends StatelessWidget {
  const _AccountTab({required this.onLogout});

  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.x4),
      children: [
        _AccountTile(
          icon: Icons.receipt_long_outlined,
          label: 'Historial de compras',
          onTap: () => context.go('/profile/orders'),
        ),
        _AccountTile(
          icon: Icons.notifications_none,
          label: 'Notificaciones',
          onTap: () => context.go('/notifications'),
        ),
        _AccountTile(
          icon: Icons.confirmation_number_outlined,
          label: 'Mis reservas',
          onTap: () => context.go('/reservations'),
        ),
        _AccountTile(
          icon: Icons.help_outline,
          label: 'Ayuda y soporte',
          onTap: () {},
        ),
        const SizedBox(height: AppSpacing.x4),
        OutlinedButton.icon(
          onPressed: () async {
            final confirmed = await showDialog<bool>(
              context: context,
              builder: (_) => AlertDialog(
                title: const Text('¿Cerrar sesión?'),
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
            if (confirmed == true) onLogout();
          },
          style: OutlinedButton.styleFrom(
            foregroundColor: AppColors.error,
            side: const BorderSide(color: AppColors.error),
          ),
          icon: const Icon(Icons.logout),
          label: const Text('Cerrar sesión'),
        ),
      ],
    );
  }
}

class _AccountTile extends StatelessWidget {
  const _AccountTile({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      margin: const EdgeInsets.only(bottom: AppSpacing.x2),
      onTap: onTap,
      child: Row(
        children: [
          Icon(icon, color: AppColors.primary),
          const SizedBox(width: AppSpacing.x3),
          Expanded(child: Text(label)),
          const Icon(Icons.chevron_right, color: AppColors.textMuted),
        ],
      ),
    );
  }
}