import 'package:flutter/material.dart';

import '../../shared/widgets/app_badge.dart';

enum ReservationStatus {
  pending('Pendiente', Icons.hourglass_empty),
  confirmed('Confirmada', Icons.check_circle_outline),
  ready('Lista para recoger', Icons.inventory_2_outlined),
  pickedUp('Recogida', Icons.shopping_bag_outlined),
  cancelled('Cancelada', Icons.cancel_outlined),
  expired('Expirada', Icons.timer_off_outlined);

  const ReservationStatus(this.label, this.icon);
  final String label;
  final IconData icon;

  AppBadgeVariant get badgeVariant => switch (this) {
        ReservationStatus.pending => AppBadgeVariant.warning,
        ReservationStatus.confirmed => AppBadgeVariant.primary,
        ReservationStatus.ready => AppBadgeVariant.primary,
        ReservationStatus.pickedUp => AppBadgeVariant.success,
        ReservationStatus.cancelled || ReservationStatus.expired =>
          AppBadgeVariant.error,
      };

  static ReservationStatus fromString(String value) {
    return ReservationStatus.values.firstWhere(
      (s) => s.name == value.toLowerCase(),
      orElse: () => ReservationStatus.pending,
    );
  }
}

class ReservationItem {
  const ReservationItem({
    required this.productId,
    required this.name,
    required this.price,
    this.variantSize,
    this.variantColor,
    this.quantity = 1,
    this.imageUrl,
  });

  final int productId;
  final String name;
  final double price;
  final String? variantSize;
  final String? variantColor;
  final int quantity;
  final String? imageUrl;

  factory ReservationItem.fromJson(Map<String, dynamic> json) {
    return ReservationItem(
      productId: json['product_id'] as int? ?? 0,
      name: json['name'] as String? ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0,
      variantSize: json['size'] as String?,
      variantColor: json['color'] as String?,
      quantity: json['quantity'] as int? ?? 1,
      imageUrl: json['image_url'] as String?,
    );
  }
}

class Reservation {
  const Reservation({
    required this.id,
    required this.status,
    required this.items,
    required this.total,
    required this.createdAt,
    this.availableUntil,
    this.branch,
    this.dueCode,
  });

  final int id;
  final ReservationStatus status;
  final List<ReservationItem> items;
  final double total;
  final DateTime createdAt;
  final DateTime? availableUntil;
  final String? branch;
  final String? dueCode;

  bool get canCancel =>
      status == ReservationStatus.pending ||
      status == ReservationStatus.confirmed;

  factory Reservation.fromJson(Map<String, dynamic> json) {
    return Reservation(
      id: json['id'] as int,
      status: ReservationStatus.fromString(
          json['status'] as String? ?? 'pending'),
      items: (json['items'] as List? ?? const [])
          .map((e) => ReservationItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num?)?.toDouble() ?? 0,
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.now(),
      availableUntil:
          DateTime.tryParse(json['available_until'] as String? ?? ''),
      branch: json['branch'] as String?,
      dueCode: json['reservation_code'] as String?,
    );
  }
}