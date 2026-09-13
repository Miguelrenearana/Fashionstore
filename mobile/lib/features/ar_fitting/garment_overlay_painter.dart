import 'dart:math' as math;

import 'package:flutter/material.dart';

/// Placeholder 2D warp overlay. In Ciclo 3 a real MediaPipe pose
/// (google_mlkit_pose_detection) will drive the warp with real assets.
/// Current implementation just centers the garment sprite.
class GarmentOverlayPainter extends CustomPainter {
  GarmentOverlayPainter({required this.placeholderSrc});

  final String placeholderSrc;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = const Color(0x55FFFFFF);
    final center = Offset(size.width / 2, size.height / 2);
    canvas.drawPath(
      Path()
        ..addRRect(RRect.fromRectAndRadius(
          Rect.fromCenter(center: center, width: size.width * 0.5, height: size.height * 0.55),
          const Radius.circular(12),
        )),
      paint,
    );

    // Escala simple: 2D affine (identidad) por ahora.
    final scale = math.min(size.width / 500, size.height / 700);
    canvas.save();
    canvas.translate(center.dx, size.height * 0.42);
    canvas.scale(scale);
    _drawPlaceholder(canvas, 'Assets/placeholders - usar imagen real en Ciclo 3');
    canvas.restore();
  }

  void _drawPlaceholder(Canvas canvas, String label) {
    final textPainter = TextPainter(
      text: TextSpan(text: label, style: const TextStyle(color: Colors.white70, fontSize: 12)),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(canvas, Offset(-textPainter.width / 2, -8));
  }

  @override
  bool shouldRepaint(covariant GarmentOverlayPainter oldDelegate) => oldDelegate.placeholderSrc != placeholderSrc;
}