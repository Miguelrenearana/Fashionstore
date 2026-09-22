import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';
import 'reservation_models.dart';

class ReservationState {
  const ReservationState({
    this.reservations = const [],
    this.isLoading = false,
    this.error,
  });

  final List<Reservation> reservations;
  final bool isLoading;
  final String? error;

  List<Reservation> get active =>
      reservations.where((r) => !r.status.name.contains('cancelled')).toList();

  ReservationState copyWith({
    List<Reservation>? reservations,
    bool? isLoading,
    String? error,
  }) {
    return ReservationState(
      reservations: reservations ?? this.reservations,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class ReservationController extends StateNotifier<ReservationState> {
  ReservationController(this._api) : super(const ReservationState()) {
    load();
  }

  final ApiClient _api;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final dynamic res = await _api.get('/reservations/me');
      // Backend returns list directly, not wrapped in {items: [...]}
      final List<dynamic> data;
      if (res is List) {
        data = List<dynamic>.from(res);
      } else if (res is Map && res['items'] is List) {
        data = List<dynamic>.from(res['items'] as List);
      } else {
        data = const [];
      }
      final reservations = data
          .map((e) => Reservation.fromJson(e as Map<String, dynamic>))
          .toList();
      state = state.copyWith(reservations: reservations, isLoading: false);
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    }
  }

  Future<void> create({
    required List<Map<String, dynamic>> items,
    int? branchId,
  }) async {
    await _api.post('/reservations', data: {
      'items': items,
      if (branchId != null) 'branch_id': branchId,
    });
    await load();
  }

  Future<void> cancel(int reservationId) async {
    await _api.patch('/reservations/$reservationId/status', data: {
      'status': 'cancelled',
    });
    await load();
  }

  Future<Reservation?> detail(int reservationId) async {
    try {
      final res = await _api
          .get('/reservations/$reservationId');
      return Reservation.fromJson(
          res['reservation'] as Map<String, dynamic>? ?? res);
    } catch (_) {
      return null;
    }
  }
}

final reservationControllerProvider =
    StateNotifierProvider<ReservationController, ReservationState>((ref) {
  return ReservationController(ref.watch(apiClientProvider));
});