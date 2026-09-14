import 'dart:async';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:google_mlkit_commons/google_mlkit_commons.dart';

import 'garment_overlay_painter.dart';
import 'pose_detector.dart';

/// Virtual fitting room (CU-19): real camera preview + MediaPipe pose
/// landmarks (shoulders/hips) + a draggable/scalable 2D garment overlay.
class ArFittingScreen extends StatefulWidget {
  const ArFittingScreen({super.key, required this.variantId});

  final int variantId;

  @override
  State<ArFittingScreen> createState() => _ArFittingScreenState();
}

class _ArFittingScreenState extends State<ArFittingScreen> {
  final _poseService = PoseService();
  CameraController? _controller;
  bool _cameraReady = false;
  bool _poseMode = true;
  bool _overlayVisible = true;
  bool _detecting = false;
  List<Offset> _landmarks = const [];
  Offset _overlayOffset = Offset.zero;
  double _overlayScale = 1.0;
  String _status = 'Inicializando cámara…';

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        setState(() => _status = 'No se encontró cámara. Probando sin ella.');
        return;
      }
      final controller = CameraController(
        cameras.first,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.yuv420,
      );
      await controller.initialize();
      if (!mounted) {
        return;
      }
      setState(() {
        _controller = controller;
        _cameraReady = true;
        _status = 'Cámara lista. Mueve la prenda para ajustarla.';
      });
      await controller.startImageStream(_onFrame);
    } catch (e) {
      if (mounted) {
        setState(() => _status = 'Cámara no disponible: $e');
      }
    }
  }

  Future<void> _onFrame(CameraImage image) async {
    if (!_poseMode || _detecting || !mounted) {
      return;
    }
    _detecting = true;
    try {
      final metadata = InputImageMetadata(
        size: Size(image.width.toDouble(), image.height.toDouble()),
        rotation: InputImageRotation.rotation0deg,
        format: InputImageFormat.nv21,
        bytesPerRow: image.planes.first.bytesPerRow,
      );
      final input = InputImage.fromBytes(
        bytes: _concatPlanes(image.planes),
        metadata: metadata,
      );
      final landmarks = await _poseService.detectLandmarks(input);
      if (!mounted) {
        return;
      }
      setState(() {
        _landmarks = [
          for (final lm in landmarks)
            Offset(lm.x / image.width, lm.y / image.height),
        ];
      });
    } catch (_) {
      // Ignore detection errors on a frame (stream keeps going).
    } finally {
      _detecting = false;
    }
  }

  Uint8List _concatPlanes(List<Plane> planes) {
    final buffer = BytesBuilder();
    for (final plane in planes) {
      buffer.add(plane.bytes);
    }
    return buffer.toBytes();
  }

  @override
  void dispose() {
    _controller?.stopImageStream();
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final camera = _controller;
    return Scaffold(
      appBar: AppBar(title: const Text('Probador virtual')),
      body: Column(
        children: [
          Expanded(
            child: GestureDetector(
              onScaleStart: (d) => _overlayOffset = _overlayOffset,
              onScaleUpdate: (d) {
                setState(() {
                  _overlayScale = (_overlayScale * d.scale).clamp(0.4, 3.0);
                  _overlayOffset += d.focalPointDelta;
                });
              },
              child: Stack(
                fit: StackFit.expand,
                children: [
                  if (_cameraReady && camera != null)
                    CameraPreview(camera)
                  else
                    const _CameraPlaceholder(),
                  if (_overlayVisible)
                    CustomPaint(
                      painter: GarmentOverlayPainter(
                        placeholderSrc: 'assets/images/placeholders/hoodie_front.png',
                        label: 'Variante #${widget.variantId}',
                        offset: _overlayOffset,
                        scale: _overlayScale,
                        landmarks: _landmarks,
                      ),
                    ),
                  Positioned(
                    top: 12,
                    left: 12,
                    child: Chip(label: Text(_status)),
                  ),
                ],
              ),
            ),
          ),
          _ControlsBar(
            poseMode: _poseMode,
            overlayVisible: _overlayVisible,
            onTogglePose: (v) => setState(() => _poseMode = v),
            onToggleOverlay: (v) => setState(() => _overlayVisible = v),
            onReset: () => setState(() {
              _overlayOffset = Offset.zero;
              _overlayScale = 1.0;
            }),
            onSnap: () => _showSnapMessage(),
          ),
        ],
      ),
    );
  }

  void _showSnapMessage() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Captura simulada (galería en Ciclo 3).')),
    );
  }
}

class _ControlsBar extends StatelessWidget {
  const _ControlsBar({
    required this.poseMode,
    required this.overlayVisible,
    required this.onTogglePose,
    required this.onToggleOverlay,
    required this.onReset,
    required this.onSnap,
  });

  final bool poseMode;
  final bool overlayVisible;
  final ValueChanged<bool> onTogglePose;
  final ValueChanged<bool> onToggleOverlay;
  final VoidCallback onReset;
  final VoidCallback onSnap;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                FilterChip(
                  label: const Text('Detectar pose'),
                  selected: poseMode,
                  onSelected: onTogglePose,
                ),
                FilterChip(
                  label: const Text('Mostrar prenda'),
                  selected: overlayVisible,
                  onSelected: onToggleOverlay,
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                TextButton.icon(
                  onPressed: onReset,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Reajustar'),
                ),
                ElevatedButton.icon(
                  onPressed: onSnap,
                  icon: const Icon(Icons.photo_camera),
                  label: const Text('Capturar'),
                ),
              ],
            ),
            const Text(
              'Arrastra para mover la prenda, pellizca para escalarla.',
              style: TextStyle(fontSize: 12, color: Colors.black54),
            ),
          ],
        ),
      ),
    );
  }
}

class _CameraPlaceholder extends StatelessWidget {
  const _CameraPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black54,
      alignment: Alignment.center,
      child: const Text(
        'Cámara no disponible\n(placeholder)',
        textAlign: TextAlign.center,
        style: TextStyle(color: Colors.white70),
      ),
    );
  }
}