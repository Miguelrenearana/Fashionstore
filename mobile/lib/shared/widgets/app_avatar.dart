import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';

import '../../core/design/design.dart';

class AppAvatar extends StatelessWidget {
  const AppAvatar({
    super.key,
    this.imageUrl,
    this.initials,
    this.size = 40,
    this.onTap,
    this.badgeCount,
  });

  final String? imageUrl;
  final String? initials;
  final double size;
  final VoidCallback? onTap;
  final int? badgeCount;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final widget = badgeCount != null
        ? Badge(
            label: Text('$badgeCount'),
            backgroundColor: AppColors.error,
            child: _avatar(theme),
          )
        : _avatar(theme);

    if (onTap == null) return widget;
    return InkWell(
      onTap: onTap,
      customBorder: const CircleBorder(),
      child: widget,
    );
  }

  Widget _avatar(ThemeData theme) {
    final hasImage = imageUrl != null && imageUrl!.isNotEmpty;
    final fallback = Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
        color: AppColors.primaryLight,
        shape: BoxShape.circle,
      ),
      alignment: Alignment.center,
      child: Text(
        _initials(),
        style: theme.textTheme.labelLarge?.copyWith(
          color: AppColors.primaryDark,
          fontWeight: FontWeight.w700,
        ),
      ),
    );

    if (!hasImage) return fallback;

    return ClipOval(
      child: CachedNetworkImage(
        imageUrl: imageUrl!,
        width: size,
        height: size,
        fit: BoxFit.cover,
        placeholder: (_, __) => fallback,
        errorWidget: (_, __, ___) => fallback,
      ),
    );
  }

  String _initials() {
    if (initials != null && initials!.isNotEmpty) return initials!;
    return 'FS';
  }
}