import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:fashionstore_mobile/features/ar_fitting/garment_overlay_painter.dart';

void main() {
  test('shouldRepaint changes when image or landmarks change', () {
    const none = <Offset>[];
    const shoulders = <Offset>[
      Offset(0.35, 0.25),
      Offset(0.65, 0.25),
      Offset(0.4, 0.6),
      Offset(0.6, 0.6),
    ];
    final a = GarmentOverlayPainter(landmarks: none);
    final b = GarmentOverlayPainter(landmarks: shoulders);
    final c = GarmentOverlayPainter(
      landmarks: shoulders,
      poseConfidence: 0.8,
    );

    expect(a.shouldRepaint(b), isTrue);
    expect(b.shouldRepaint(c), isTrue);
    expect(a.shouldRepaint(a), isFalse);
  });

  testWidgets('paints without throwing with no pose', (tester) async {
    final image = _solidGarment(32, 40);
    await tester.pumpWidget(
      MaterialApp(
        home: CustomPaint(
          size: const Size(400, 600),
          painter: GarmentOverlayPainter(garmentImage: image),
        ),
      ),
    );
    expect(tester.takeException(), isNull);
    image.dispose();
  });

  testWidgets('paints with torso quad for anchored garment', (tester) async {
    final image = _solidGarment(32, 40);
    const landmarks = <Offset>[
      Offset(0.4, 0.2),
      Offset(0.6, 0.2),
      Offset(0.42, 0.55),
      Offset(0.58, 0.55),
    ];
    await tester.pumpWidget(
      MaterialApp(
        home: CustomPaint(
          size: const Size(400, 600),
          painter: GarmentOverlayPainter(
            garmentImage: image,
            landmarks: landmarks,
            poseConfidence: 0.9,
          ),
        ),
      ),
    );
    expect(tester.takeException(), isNull);
    image.dispose();
  });
}

ui.Image _solidGarment(int w, int h) {
  final recorder = ui.PictureRecorder();
  final canvas = Canvas(recorder);
  canvas.drawRect(
    const Rect.fromLTWH(0, 0, 100, 100),
    Paint()..color = const Color(0xFFFF8C00),
  );
  final picture = recorder.endRecording();
  final image = picture.toImageSync(w, h);
  picture.dispose();
  return image;
}