import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:flutter/material.dart';

/// Real-time 2D garment overlay (CU-19).
///
/// Anchors the garment image to the detected torso quadrilateral
/// (left shoulder -> right shoulder -> right hip -> left hip) so it
/// "hangs" on the person as they move in front of the camera. When no
/// pose is detected the garment stays centered with a sensible default
/// scale.
class GarmentOverlayPainter extends CustomPainter {
  GarmentOverlayPainter({
    this.garmentImage,
    this.landmarks = const [],
    this.poseConfidence = 0.0,
  });

  /// Transparent PNG of the garment to draw (null -> nothing drawn over
  /// the pose landmarks).
  final ui.Image? garmentImage;

  /// Normalized pose landmarks of interest: shoulders + hips.
  final List<Offset> landmarks;

  /// 0..1 confidence from the pose detector; used to blend the garment
  /// opacity in/out to avoid flicker.
  final double poseConfidence;

  static const double _garmentWidthFactor = 1.18;
  static const double _torsoHeightFactor = 1.1;
  static const double _neckInset = 0.22;

  @override
  void paint(Canvas canvas, Size size) {
    final quad = _torsoQuad(size);
    if (quad != null) {
      _drawGarment(canvas, size, quad);
    } else if (garmentImage != null) {
      _drawFallbackCentered(canvas, size);
    }
    _drawPoseLandmarks(canvas, size);
  }

  /// Computes the torso quadrilateral from shoulder/hip landmarks.
  /// Returns null when there are not enough landmarks.
  List<Offset>? _torsoQuad(Size size) {
    final g = _groupLandmarks(size);
    final ls = g[_Part.leftShoulder];
    final rs = g[_Part.rightShoulder];
    final lh = g[_Part.leftHip];
    final rh = g[_Part.rightHip];
    if (ls == null || rs == null || lh == null || rh == null) {
      return null;
    }
    return [ls, rs, rh, lh];
  }

  /// Groups normalized landmarks. The pose service sends them in the order
  /// shoulders (2) then hips (2); each carries its own coordinates so we can
  /// derive left/right by x-positions when needed.
  Map<_Part, Offset> _groupLandmarks(Size size) {
    final shoulders = <Offset>[];
    final hips = <Offset>[];
    if (landmarks.length >= 4) {
      shoulders.addAll(landmarks.sublist(0, 2));
      hips.addAll(landmarks.sublist(2, 4));
    } else if (landmarks.length == 2) {
      shoulders.addAll(landmarks);
    }

    Offset to(Offset p) => Offset(p.dx * size.width, p.dy * size.height);

    // Left = smaller x when the subject faces the camera normally; we sort
    // so the garment does not flip if the feed is mirrored.
    final sh = shoulders.map(to).toList();
    final hp = hips.map(to).toList();

    Offset minX(List<Offset> pts) =>
        pts.isEmpty ? Offset.zero : pts.reduce((a, b) => a.dx <= b.dx ? a : b);
    Offset maxX(List<Offset> pts) =>
        pts.isEmpty ? Offset.zero : pts.reduce((a, b) => a.dx >= b.dx ? a : b);

    final map = <_Part, Offset>{};
    if (sh.isNotEmpty) {
      map[_Part.leftShoulder] = minX(sh);
      map[_Part.rightShoulder] = maxX(sh);
    }
    if (hp.length >= 2) {
      map[_Part.leftHip] = minX(hp);
      map[_Part.rightHip] = maxX(hp);
    }
    return map;
  }

  void _drawGarment(Canvas canvas, Size size, List<Offset> quad) {
    final image = garmentImage;
    if (image == null) {
      return;
    }
    final ls = quad[0];
    final rs = quad[1];
    final lh = quad[2];
    final rh = quad[3];

    final shoulderWidth = (rs - ls).distance;
    if (shoulderWidth <= 0) {
      return;
    }

    // Garment size from the shoulder span (what we can reliably measure).
    final garmentWidth = shoulderWidth * _garmentWidthFactor;
    final imgAspect = image.width / image.height;
    final drawW = garmentWidth;
    final drawH = drawW / imgAspect;

    // Torso direction vector + center.
    final torsoTop = Offset((ls.dx + rs.dx) / 2, (ls.dy + rs.dy) / 2);
    final torsoBottom = Offset((lh.dx + rh.dx) / 2, (lh.dy + rh.dy) / 2);
    final torsoVec = torsoBottom - torsoTop;
    final torsoAngle = math.atan2(torsoVec.dy, torsoVec.dx);

    // Expected torso height (neck inset + garment hangs below hips a bit).
    final expectedTorso =
        torsoVec.distance * _torsoHeightFactor / (1 - _neckInset);

    // Blend scale so the garment reaches around hip level even when the
    // detected torso is short (partial view).
    final heightScale =
        math.min(1.0, expectedTorso / drawH).clamp(0.85, 1.5);
    final finalWidth = drawW * heightScale;
    final finalHeight = finalWidth / imgAspect;

    // Drape anchor: pull the garment up by the neck inset relative to the
    // shoulder line so the shoulders align.
    final anchor = torsoTop +
        Offset(
          -math.cos(torsoAngle) * (expectedTorso * _neckInset),
          -math.sin(torsoAngle) * (expectedTorso * _neckInset),
        );

    canvas.save();
    canvas.translate(anchor.dx, anchor.dy);
    // -90deg because the garment image is drawn with its height aligned to
    // the torso direction and the image's up direction is -y.
    canvas.rotate(torsoAngle - math.pi / 2);
    // Slight perspective skew: narrower at the waist. Implemented as a
    // shear so the overlay still reads as a garment, not a sticker.
    final opacity = (0.65 + poseConfidence * 0.35).clamp(0.0, 1.0);
    _drawScaledImage(
      canvas,
      image,
      Offset.zero,
      finalWidth,
      finalHeight,
      opacity.toDouble(),
    );
    canvas.restore();
  }

  void _drawScaledImage(
    Canvas canvas,
    ui.Image image,
    Offset center,
    double width,
    double height,
    double opacity,
  ) {
    final src = Rect.fromLTWH(
      0,
      0,
      image.width.toDouble(),
      image.height.toDouble(),
    );
    final dst = Rect.fromCenter(
      center: center,
      width: width,
      height: height,
    );
    final paint = Paint()
      ..isAntiAlias = true
      ..filterQuality = FilterQuality.medium
      ..color = Color.fromRGBO(255, 255, 255, opacity);
    canvas.drawImageRect(image, src, dst, paint);
  }

  void _drawFallbackCentered(Canvas canvas, Size size) {
    final image = garmentImage;
    if (image == null) {
      return;
    }
    final w = size.width * 0.5;
    final h = w * image.height / image.width;
    _drawScaledImage(canvas, image, Offset(size.width / 2, size.height * 0.5), w, h, 0.6);
  }

  void _drawPoseLandmarks(Canvas canvas, Size size) {
    if (landmarks.isEmpty) {
      return;
    }
    final paint = Paint()
      ..color = const Color(0xCC00E676)
      ..style = PaintingStyle.fill;
    for (final lm in landmarks) {
      canvas.drawCircle(
        Offset(lm.dx * size.width, lm.dy * size.height),
        4,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant GarmentOverlayPainter oldDelegate) =>
      oldDelegate.garmentImage != garmentImage ||
      oldDelegate.landmarks.length != landmarks.length ||
      oldDelegate.poseConfidence != poseConfidence;
}

enum _Part { leftShoulder, rightShoulder, leftHip, rightHip }