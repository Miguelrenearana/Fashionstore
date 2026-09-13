import 'package:flutter/material.dart';

import 'garment_overlay_painter.dart';

/// Proves virtual fitting screen (Ciclo 1):
/// shows the camera feed placeholder + a 2D garment overlay.
class ArFittingScreen extends StatefulWidget {
  const ArFittingScreen({super.key, required this.variantId});

  final int variantId;

  @override
  State<ArFittingScreen> createState() => _ArFittingScreenState();
}

class _ArFittingScreenState extends State<ArFittingScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Probador virtual')),
      body: Stack(
        children: [
          const Positioned.fill(child: CameraPlaceholder()),
          Positioned.fill(
            child: CustomPaint(painter: GarmentOverlayPainter(placeholderSrc: 'assets/images/placeholders/hoodie_front.png')),
          ),
          Positioned(
            bottom: 24,
            left: 24,
            right: 24,
            child: Text(
              'Variante #${widget.variantId} — arrastra para ajustar',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }
}

class CameraPlaceholder extends StatelessWidget {
  const CameraPlaceholder({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(color: Colors.black54);
  }
}