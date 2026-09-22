class Promotion {
  const Promotion({
    required this.id,
    required this.name,
    required this.discountPercent,
    required this.startAt,
    required this.endAt,
    this.description,
    this.status,
    this.garmentIds = const [],
  });

  final int id;
  final String name;
  final double discountPercent;
  final DateTime startAt;
  final DateTime endAt;
  final String? description;
  final String? status;
  final List<int> garmentIds;

  factory Promotion.fromJson(Map<String, dynamic> json) {
    return Promotion(
      id: (json['id'] as num?)?.toInt() ?? 0,
      name: (json['name'] as String?) ?? '',
      discountPercent: (json['discount_percent'] as num?)?.toDouble() ?? 0,
      startAt: DateTime.tryParse((json['start_at'] as String?) ?? '') ??
          DateTime.now(),
      endAt: DateTime.tryParse((json['end_at'] as String?) ?? '') ??
          DateTime.now(),
      description: json['description'] as String?,
      status: json['status'] as String?,
      garmentIds: ((json['garment_ids'] as List?) ?? const [])
          .map((e) => (e as num).toInt())
          .toList(),
    );
  }
}
