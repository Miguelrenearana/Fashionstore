import 'dart:math' as math;

import 'package:flutter/material.dart';

/// Placeholder 2D warp overlay. In Ciclo 3 a real MediaPipe pose
/// (google_mlkit_pose_detection) will drive the warp with real assets.
/// Supports manual drag/scale from the fitting room screen and draws the
/// detected landmarks (shoulders/hips) as reference dots.
class GarmentOverlayPainter extends CustomPainter {
  GarmentOverlayPainter({
    required this.placeholderSrc,
    this.label = '',
    this.offset = Offset.zero,
    this.scale = 1.0,
    this.landmarks = const [],
  });

  final String placeholderSrc;
  final String label;
  final Offset offset;
  final double scale;
  final List<Offset> landmarks;

  @override
  void paint(Canvas canvas, Size size) {
    _drawPoseLandmarks(canvas, size);

    final paint = Paint()..color = const Color(0x33FFFFFF);
    final center = Offset(size.width / 2, size.height / 2) + offset;
    canvas.drawPath(
      Path()
        ..addRRect(RRect.fromRectAndRadius(
          Rect.fromCenter(
              center: center, width: size.width * 0.5 * scale, height: size.height * 0.55 * scale),
          const Radius.circular(12),
        )),
      paint,
    );

    final spriteScale = math.min(size.width / 500, size.height / 700) * scale;
    canvas.save();
    canvas.translate(center.dx, size.height * 0.42 + offset.dy);
    canvas.scale(spriteScale);
    _drawPlaceholder(canvas, label.isEmpty ? placeholderSrc : label);
    canvas.restore();
  }

  void _drawPoseLandmarks(Canvas canvas, Size size) {
    if (landmarks.isEmpty) {
      return;
    }
    final paint = Paint()
      ..color = const Color(0xCC00E676)
      ..strokeWidth = 3
      ..style = PaintingStyle.fill;
    for (final lm in landmarks) {
      canvas.drawCircle(Offset(lm.dx * size.width, lm.dy * size.height), 6, paint);
    }
  }

  void _drawPlaceholder(Canvas canvas, String label) {
    final textPainter = TextPainter(
      text: TextSpan(text: label, style: const TextStyle(color: Colors.white70, fontSize: 12)),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(canvas, Offset(-textPainter.width / 2, -8));
  }

  @override
  bool shouldRepaint(covariant GarmentOverlayPainter oldDelegate) =>
      oldDelegate.placeholderSrc != placeholderSrc ||
      oldDelegate.offset != offset ||
      oldDelegate.scale != scale ||
      oldDelegate.landmarks != landmarks;
}