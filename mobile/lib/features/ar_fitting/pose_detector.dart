import 'package:flutter/widgets.dart';
import 'package:google_mlkit_pose_detection/google_mlkit_pose_detection.dart';

/// Normalized (0..1 relative to the frame) pose of the torso.
class DetectedPose {
  const DetectedPose({
    this.leftShoulder,
    this.rightShoulder,
    this.leftHip,
    this.rightHip,
    this.confidence = 0.0,
  });

  /// Offset in normalized frame coords, or null when the joint was not found.
  final Offset? leftShoulder;
  final Offset? rightShoulder;
  final Offset? leftHip;
  final Offset? rightHip;

  /// 0..1 model confidence (best of the available joints).
  final double confidence;

  bool get hasTorso =>
      leftShoulder != null &&
      rightShoulder != null &&
      leftHip != null &&
      rightHip != null;

  /// Landmarks in painter order: shoulders then hips (normalized).
  List<Offset> get landmarks => [
        if (leftShoulder != null) leftShoulder!,
        if (rightShoulder != null) rightShoulder!,
        if (leftHip != null) leftHip!,
        if (rightHip != null) rightHip!,
      ];
}

/// Abstraction over MediaPipe pose detection (google_mlkit).
///
/// Drives the 2D garment warp of the AR fitting room with real
/// shoulder/hip landmarks.
class PoseService {
  PoseService({this.mode = PoseDetectionMode.stream});

  final PoseDetectionMode mode;
  PoseDetectorOptions? _options;

  PoseDetectorOptions get options =>
      _options ??= PoseDetectorOptions(mode: mode);

  /// Runs pose detection on a camera frame and returns the normalized torso.
  Future<DetectedPose> detectTorso(InputImage input,
      {required Size frameSize}) async {
    final detector = PoseDetector(options: options);
    final poses = await detector.processImage(input);
    detector.close();

    if (poses.isEmpty) {
      return const DetectedPose();
    }
    final pose = poses.first;

    Offset? norm(PoseLandmarkType type) {
      final lm = pose.landmarks[type];
      if (lm == null || frameSize.width <= 0 || frameSize.height <= 0) {
        return null;
      }
      return Offset(lm.x / frameSize.width, lm.y / frameSize.height);
    }

    final shoulders = <Offset?>{
      norm(PoseLandmarkType.leftShoulder),
      norm(PoseLandmarkType.rightShoulder),
    };
    final hips = <Offset?>{
      norm(PoseLandmarkType.leftHip),
      norm(PoseLandmarkType.rightHip),
    };

    // Confidence signal: fraction of the four torso joints detected.
    final joints = <Offset?>[...shoulders, ...hips];
    final found = joints.where((j) => j != null).length;
    final confidence = joints.isEmpty ? 0.0 : found / joints.length;

    return DetectedPose(
      leftShoulder: shoulders.elementAt(0),
      rightShoulder: shoulders.elementAt(1),
      leftHip: hips.elementAt(0),
      rightHip: hips.elementAt(1),
      confidence: confidence,
    );
  }
}