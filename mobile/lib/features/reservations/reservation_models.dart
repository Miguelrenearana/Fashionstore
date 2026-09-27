import 'package:flutter/material.dart';

import '../../shared/widgets/app_badge.dart';

/// Estados reales de `reserva.status` en el backend.
enum ReservationStatus {
  pending('Pendiente', 'PENDING', Icons.hourglass_empty),
  prepared('En preparación', 'PREPARED', Icons.check_circle_outline),
  inTrial('En prueba', 'IN_TRIAL', Icons.straighten_outlined),
  completed('Completada', 'COMPLETED', Icons.shopping_bag_outlined),
  cancelled('Cancelada', 'CANCELLED', Icons.cancel_outlined),
  expired('Expirada', 'EXPIRED', Icons.timer_off_outlined);

  const ReservationStatus(this.label, this.wireValue, this.icon);

  final String label;

  /// Valor exacto que espera la API al cambiar el estado.
  final String wireValue;
  final IconData icon;

  AppBadgeVariant get badgeVariant => switch (this) {
        ReservationStatus.pending => AppBadgeVariant.warning,
        ReservationStatus.prepared => AppBadgeVariant.primary,
        ReservationStatus.inTrial => AppBadgeVariant.primary,
        ReservationStatus.completed => AppBadgeVariant.success,
        ReservationStatus.cancelled || ReservationStatus.expired =>
          AppBadgeVariant.error,
      };

  bool get isFinal =>
      this == completed || this == cancelled || this == expired;

  static ReservationStatus fromString(String value) {
    final v = value.trim().toUpperCase();
    return ReservationStatus.values.firstWhere(
      (s) => s.wireValue == v,
      orElse: () => ReservationStatus.pending,
    );
  }
}

class ReservationItem {
  const ReservationItem({
    required this.variantId,
    required this.quantity,
    required this.unitPrice,
    this.garmentId,
    this.name,
    this.variantSize,
    this.variantColor,
    this.imageUrl,
    this.available = 0,
  });

  final int variantId;
  final int quantity;
  final double unitPrice;
  final int? garmentId;
  final String? name;
  final String? variantSize;
  final String? variantColor;
  final String? imageUrl;

  /// Disponibilidad de la variante en la sucursal de la reserva (CU-14).
  final int available;

  double get subtotal => unitPrice * quantity;

  factory ReservationItem.fromJson(Map<String, dynamic> json) {
    return ReservationItem(
      variantId: (json['variant_id'] as num?)?.toInt() ?? 0,
      quantity: (json['quantity'] as num?)?.toInt() ?? 1,
      unitPrice: (json['unit_price'] as num?)?.toDouble() ?? 0,
      garmentId: (json['garment_id'] as num?)?.toInt(),
      name: json['product_name'] as String?,
      variantSize: json['size_name'] as String?,
      variantColor: json['color_name'] as String?,
      imageUrl: json['image_url'] as String?,
      available: (json['available'] as num?)?.toInt() ?? 0,
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
    this.branchId,
    this.branchName,
    this.dueCode,
  });

  final int id;
  final ReservationStatus status;
  final List<ReservationItem> items;
  final double total;
  final DateTime createdAt;
  final DateTime? availableUntil;
  final int? branchId;
  final String? branchName;
  final String? dueCode;

  /// El cliente solo puede cancelar mientras siga pendiente o en preparacion.
  bool get canCancel =>
      status == ReservationStatus.pending ||
      status == ReservationStatus.prepared;

  factory Reservation.fromJson(Map<String, dynamic> json) {
    // El backend expone `details`; `items` es el alias que consume el movil.
    final rawItems = (json['items'] ?? json['details']) as List? ?? const [];
    return Reservation(
      id: (json['id'] as num).toInt(),
      status: ReservationStatus.fromString(json['status'] as String? ?? 'PENDING'),
      items: rawItems
          .map((e) => ReservationItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] ?? json['total_amount'] as num?)?.toDouble() ?? 0,
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.now(),
      availableUntil:
          DateTime.tryParse(json['available_until'] ?? json['expires_at'] as String? ?? ''),
      branchId: (json['branch_id'] as num?)?.toInt(),
      branchName: json['branch_name'] as String?,
      dueCode: (json['reservation_code'] ?? json['pickup_code']) as String?,
    );
  }
}