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
      reservations.where((r) => !r.status.isFinal).toList();

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
  bool _creating = false;
  int _loadVersion = 0;

  Future<void> load() async {
    final version = ++_loadVersion;
    state = state.copyWith(isLoading: true, error: null);
    try {
      final data = await _api.getList('/reservations/me');
      final reservations = data
          .map((e) => Reservation.fromJson(e as Map<String, dynamic>))
          .toList();
      if (mounted && version == _loadVersion) {
        state = state.copyWith(reservations: reservations);
      }
    } catch (e) {
      if (mounted && version == _loadVersion) {
        state = state.copyWith(error: e is ApiException ? e.message :
          'No se pudo interpretar la respuesta de reservas.');
      }
    } finally {
      if (mounted && version == _loadVersion) {
        state = state.copyWith(isLoading: false, error: state.error);
      }
    }
  }

  Future<void> create({
    required List<Map<String, dynamic>> items,
    required int branchId,
    String? notes,
  }) async {
    if (_creating) {
      throw ApiException('La reserva está en curso.');
    }
    _creating = true;
    ++_loadVersion;
    try {
      final reservation = await _api.createOnce('/reservations', data: {
        'branch_id': branchId,
        'items': items,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      }, decode: Reservation.fromJson);
      ++_loadVersion;
      if (mounted) {
        state = state.copyWith(isLoading: false, reservations: [reservation,
          ...state.reservations.where((r) => r.id != reservation.id)]);
      }
    } catch (_) {
      await load(); // Consultar; nunca repetir el POST tras respuesta perdida.
      rethrow;
    } finally {
      _creating = false;
    }
  }

  /// Cancela la reserva. El backend exige el estado en mayusculas.
  Future<void> cancel(int reservationId) async {
    await _api.patch(
      '/reservations/$reservationId/status',
      data: {'status': ReservationStatus.cancelled.wireValue},
    );
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
