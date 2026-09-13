import 'package:google_mlkit_pose_detection/google_mlkit_pose_detection.dart';

/// Abstraction over MediaPipe pose detection (google_mlkit).
/// Ciclo 1-2: placeholders (no se procesan landmarks); Ciclo 3 (pausado):
/// los landmarks del pose dirigirán el warp 2D de la prenda con assets reales.
class PoseService {
  PoseService({this.mode = PoseDetectionMode.stream});

  final PoseDetectionMode mode;
  PoseDetectorOptions? _options;

  PoseDetectorOptions get options =>
      _options ??= PoseDetectorOptions(mode: mode);

  /// Runs pose detection on a camera frame. Returns landmarks of interest
  /// (shoulders + hips) as a list, or an empty list if no pose found.
  Future<List<PoseLandmark>> detectLandmarks(InputImage input) async {
    final detector = PoseDetector(options: options);
    final poses = await detector.processImage(input);
    detector.close();

    final landmarks = <PoseLandmark>[];
    for (final pose in poses) {
      final shoulders = {
        PoseLandmarkType.leftShoulder,
        PoseLandmarkType.rightShoulder,
        PoseLandmarkType.leftHip,
        PoseLandmarkType.rightHip,
      };
      landmarks.addAll(
        pose.landmarks.entries
            .where((e) => shoulders.contains(e.key))
            .map((e) => e.value),
      );
    }
    return landmarks;
  }
}