import 'dart:async';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mlkit_commons/google_mlkit_commons.dart';

import '../../core/di/providers.dart';
import 'garment_overlay_painter.dart';
import 'pose_detector.dart';

/// Virtual fitting room (CU-19): real camera preview + MediaPipe pose
/// landmarks (shoulders/hips) + the selected garment auto-anchored to the
/// detected torso.
class ArFittingScreen extends ConsumerStatefulWidget {
  const ArFittingScreen({super.key, required this.variantId});

  final int variantId;

  @override
  ConsumerState<ArFittingScreen> createState() => _ArFittingScreenState();
}

class _ArFittingScreenState extends ConsumerState<ArFittingScreen> {
  final _poseService = PoseService();
  CameraController? _controller;
  bool _cameraReady = false;
  bool _poseMode = true;
  bool _detecting = false;

  final _garmentAssets = <String, String>{
    'camiseta': 'assets/images/garments/camiseta.png',
    'playera': 'assets/images/garments/playera.png',
    'hoodie': 'assets/images/garments/hoodie.png',
    'vestido': 'assets/images/garments/vestido.png',
    'chaqueta': 'assets/images/garments/chaqueta.png',
    'blusa': 'assets/images/garments/blusa.png',
  };
  final Map<String, ui.Image> _loadedGarments = {};
  String _selectedGarment = 'camiseta';
  String _garmentName = '';
  DetectedPose _pose = const DetectedPose();
  String _status = 'Inicializando cámara…';

  @override
  void initState() {
    super.initState();
    _initCamera();
    _loadArConfig();
    _loadGarmentImages();
  }

  Future<void> _loadGarmentImages() async {
    for (final entry in _garmentAssets.entries) {
      try {
        final data = await DefaultAssetBundle.of(context).load(entry.value);
        final codec = await ui.instantiateImageCodec(data.buffer.asUint8List());
        final frame = await codec.getNextFrame();
        _loadedGarments[entry.key] = frame.image;
      } catch (_) {
        // Keep the garment unavailable if its asset cannot be decoded.
      }
    }
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _loadArConfig() async {
    try {
      final data = await ref
          .read(apiClientProvider)
          .get('/catalog/${widget.variantId}/ar-config');
      if (mounted) {
        setState(() {
          _garmentName = (data['garment_name'] as String?) ?? '';
        });
      }
    } catch (_) {
      // Keep the placeholder label if the AR config is unavailable.
    }
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
        _status = 'Cámara lista. Colócate frente a la cámara.';
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
      final pose = await _poseService.detectTorso(
        input,
        frameSize: Size(image.width.toDouble(), image.height.toDouble()),
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _pose = pose;
        _status = pose.hasTorso
            ? 'Prenda anclada. Muévete para verla caer.'
            : 'No se detectó el torso completo.';
      });
    } catch (_) {
      // Ignore detection errors on a frame (stream keeps going).
    } finally {
      _detecting = false;
    }
  }

  Uint8List _concatPlanes(List<Plane> planes) {
    final builder = BytesBuilder();
    for (final plane in planes) {
      builder.add(plane.bytes);
    }
    return builder.toBytes();
  }

  @override
  void dispose() {
    _controller?.stopImageStream();
    _controller?.dispose();
    for (final image in _loadedGarments.values) {
      image.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final camera = _controller;
    final garmentImage = _loadedGarments[_selectedGarment];
    return Scaffold(
      appBar: AppBar(title: const Text('Probador virtual')),
      body: Column(
        children: [
          Expanded(
            child: Stack(
              fit: StackFit.expand,
              children: [
                if (_cameraReady && camera != null)
                  CameraPreview(camera)
                else
                  const _CameraPlaceholder(),
                if (garmentImage != null)
                  CustomPaint(
                    painter: GarmentOverlayPainter(
                      garmentImage: garmentImage,
                      landmarks: _pose.landmarks,
                      poseConfidence: _pose.confidence,
                    ),
                  ),
                Positioned(
                  top: 12,
                  left: 12,
                  child: Chip(
                    label: Text(
                      _garmentName.isNotEmpty
                          ? '$_garmentName · $_selectedGarment'
                          : _selectedGarment,
                    ),
                  ),
                ),
              ],
            ),
          ),
          _ControlsBar(
            poseMode: _poseMode,
            onTogglePose: (v) => setState(() => _poseMode = v),
            onSnap: () => _showSnapMessage(),
          ),
          _GarmentPicker(
            garments: _garmentAssets.keys.toList(),
            selected: _selectedGarment,
            loaded: _loadedGarments,
            onSelected: (name) => setState(() => _selectedGarment = name),
          ),
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              _status,
              style: const TextStyle(fontSize: 12, color: Colors.black54),
              textAlign: TextAlign.center,
            ),
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
    required this.onTogglePose,
    required this.onSnap,
  });

  final bool poseMode;
  final ValueChanged<bool> onTogglePose;
  final VoidCallback onSnap;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            FilterChip(
              label: const Text('Detectar pose'),
              selected: poseMode,
              onSelected: onTogglePose,
            ),
            ElevatedButton.icon(
              onPressed: onSnap,
              icon: const Icon(Icons.photo_camera),
              label: const Text('Capturar'),
            ),
          ],
        ),
      ),
    );
  }
}

class _GarmentPicker extends StatelessWidget {
  const _GarmentPicker({
    required this.garments,
    required this.selected,
    required this.loaded,
    required this.onSelected,
  });

  final List<String> garments;
  final String selected;
  final Map<String, ui.Image> loaded;
  final ValueChanged<String> onSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 76,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        itemCount: garments.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final name = garments[index];
          final image = loaded[name];
          final isSelected = name == selected;
          return InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => onSelected(name),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              width: 64,
              decoration: BoxDecoration(
                color: isSelected
                    ? Theme.of(context).colorScheme.primaryContainer
                    : Colors.grey.shade100,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isSelected
                      ? Theme.of(context).colorScheme.primary
                      : Colors.transparent,
                  width: 2,
                ),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (image != null)
                    SizedBox(
                      width: 40,
                      height: 40,
                      child: CustomPaint(
                        painter: _ThumbPainter(image),
                      ),
                    )
                  else
                    const SizedBox(
                      width: 40,
                      height: 40,
                      child: Icon(Icons.checkroom, size: 28),
                    ),
                  const SizedBox(height: 2),
                  Text(
                    name,
                    style: const TextStyle(fontSize: 10),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _ThumbPainter extends CustomPainter {
  _ThumbPainter(this.image);

  final ui.Image image;

  @override
  void paint(Canvas canvas, Size size) {
    final src = Rect.fromLTWH(
      0,
      0,
      image.width.toDouble(),
      image.height.toDouble(),
    );
    canvas.drawImageRect(
      image,
      src,
      Offset.zero & size,
      Paint()
        ..isAntiAlias = true
        ..filterQuality = FilterQuality.low,
    );
  }

  @override
  bool shouldRepaint(covariant _ThumbPainter oldDelegate) =>
      oldDelegate.image != image;
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