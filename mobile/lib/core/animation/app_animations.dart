import 'package:flutter/material.dart';

class AppAnimations {
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration base = Duration(milliseconds: 200);
  static const Duration slow = Duration(milliseconds: 300);

  static Curve get easeOut => Curves.easeOutCubic;
  static Curve get easeIn => Curves.easeInCubic;
  static Curve get easeInOut => Curves.easeInOutCubic;

  // Fade
  static Widget fadeIn({required Widget child, Duration duration = base}) {
    return AnimatedOpacity(
      opacity: 1.0,
      duration: duration,
      curve: easeOut,
      child: child,
    );
  }

  // Slide Up
  static Widget slideUp({required Widget child, Duration duration = base, double offset = 20}) {
    return TweenAnimationBuilder<Offset>(
      tween: Tween(begin: Offset(0.0, offset), end: Offset.zero),
      duration: duration,
      curve: easeOut,
      builder: (context, value, child) => Transform.translate(
        offset: Offset(0.0, value.dx - offset),
        child: child,
      ),
      child: child,
    );
  }

  // Scale Tap
  static Widget scaleTap({required Widget child, required VoidCallback onTap}) {
    return GestureDetector(
      onTapDown: (_) => {},
      onTapUp: (_) => onTap(),
      onTapCancel: () => {},
      child: AnimatedScale(
        scale: 1.0,
        duration: Duration(milliseconds: 100),
        curve: Curves.easeOut,
        child: child,
      ),
    );
  }

  // Shimmer
  static Widget shimmer({required Widget child}) {
    return ShaderMask(
      shaderCallback: (bounds) => LinearGradient(
        colors: [Colors.grey[300]!, Colors.grey[100]!, Colors.grey[300]!],
        stops: [0.1, 0.5, 0.9],
        transform: GradientRotation(0.5),
      ).createShader(bounds),
      blendMode: BlendMode.srcATop,
      child: child,
    );
  }

  // Stagger List
  static List<Widget> stagger(List<Widget> children, {Duration delay = const Duration(milliseconds: 100)}) {
    return children.asMap().entries.map((entry) {
      final index = entry.key;
      final child = entry.value;
      return TweenAnimationBuilder<double>(
        tween: Tween(begin: 0.0, end: 1.0),
        duration: Duration(milliseconds: 300 + index * delay.inMilliseconds),
        curve: Curves.easeOut,
        builder: (context, value, child) => Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0.0, 20.0 * (1.0 - value)),
            child: child,
          ),
        ),
        child: child,
      );
    }).toList();
  }
}