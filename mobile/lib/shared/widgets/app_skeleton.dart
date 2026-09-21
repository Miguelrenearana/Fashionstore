import 'package:flutter/material.dart';

import '../../core/design/design.dart';
import 'app_card.dart';

class AppSkeleton extends StatefulWidget {
  const AppSkeleton({
    super.key,
    this.width,
    this.height = 14,
    this.shape = BoxShape.rectangle,
    this.borderRadius = AppRadius.md,
  });

  final double? width;
  final double height;
  final BoxShape shape;
  final double borderRadius;

  @override
  State<AppSkeleton> createState() => _AppSkeletonState();
}

class _AppSkeletonState extends State<AppSkeleton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1200),
  )..repeat();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final base = theme.brightness == Brightness.dark
        ? AppColors.darkSurfaceAlt
        : AppColors.surfaceAlt;

    return AnimatedBuilder(
      animation: _controller,
      builder: (_, child) {
        return ShaderMask(
          blendMode: BlendMode.srcATop,
          shaderCallback: (bounds) {
            final shift = (_controller.value * 2 - 1) * bounds.width;
            return LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                base,
                AppColors.surface,
                base,
              ],
              stops: const [0.35, 0.55, 0.75],
              transform:
                  _SlideGradientTransform(translateX: shift),
            ).createShader(bounds);
          },
          child: child,
        );
      },
      child: Container(
        width: widget.width,
        height: widget.height,
        decoration: widget.shape == BoxShape.circle
            ? const BoxDecoration(color: AppColors.surfaceAlt, shape: BoxShape.circle)
            : BoxDecoration(
                color: AppColors.surfaceAlt,
                borderRadius: BorderRadius.circular(widget.borderRadius),
              ),
      ),
    );
  }
}

class _SlideGradientTransform extends GradientTransform {
  const _SlideGradientTransform({required this.translateX});

  final double translateX;

  @override
  Matrix4? transform(Rect bounds, {TextDirection? textDirection}) =>
      Matrix4.translationValues(translateX, 0, 0);
}

class AppSkeletonCard extends StatelessWidget {
  const AppSkeletonCard({super.key, this.showImage = true});

  final bool showImage;

  @override
  Widget build(BuildContext context) {
    return const AppCard(
      bordered: true,
      padding: EdgeInsets.all(AppSpacing.x4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppSkeleton(height: 16),
          SizedBox(height: AppSpacing.x3),
          AppSkeleton(width: 140),
          SizedBox(height: AppSpacing.x2),
          AppSkeleton(width: 90),
        ],
      ),
    );
  }
}