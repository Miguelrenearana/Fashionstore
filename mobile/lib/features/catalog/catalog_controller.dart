import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/catalog.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';

class CatalogFilter {
  const CatalogFilter({
    this.search = '',
    this.categoryId,
    this.branchId,
    this.minPrice,
    this.maxPrice,
    this.sizes = const {},
    this.colors = const {},
    this.inStockOnly = false,
    this.sortBy,
  });

  final String search;
  final int? categoryId;

  /// CU-14: sucursal seleccionada para consultar disponibilidad.
  final int? branchId;
  final double? minPrice;
  final double? maxPrice;
  final Set<String> sizes;
  final Set<String> colors;
  final bool inStockOnly;
  final String? sortBy;

  bool get hasActiveFilters =>
      search.isNotEmpty ||
      categoryId != null ||
      branchId != null ||
      minPrice != null ||
      maxPrice != null ||
      sizes.isNotEmpty ||
      colors.isNotEmpty ||
      inStockOnly;

  CatalogFilter copyWith({
    String? search,
    int? categoryId,
    int? branchId,
    double? minPrice,
    double? maxPrice,
    Set<String>? sizes,
    Set<String>? colors,
    bool? inStockOnly,
    String? sortBy,
  }) {
    return CatalogFilter(
      search: search ?? this.search,
      categoryId: categoryId ?? this.categoryId,
      branchId: branchId ?? this.branchId,
      minPrice: minPrice ?? this.minPrice,
      maxPrice: maxPrice ?? this.maxPrice,
      sizes: sizes ?? this.sizes,
      colors: colors ?? this.colors,
      inStockOnly: inStockOnly ?? this.inStockOnly,
      sortBy: sortBy ?? this.sortBy,
    );
  }

  /// Unlike [copyWith], this allows clearing the branch (back to "all branches").
  CatalogFilter withBranch(int? branchId) => CatalogFilter(
        search: search,
        categoryId: categoryId,
        branchId: branchId,
        minPrice: minPrice,
        maxPrice: maxPrice,
        sizes: sizes,
        colors: colors,
        inStockOnly: inStockOnly,
        sortBy: sortBy,
      );
}

class CatalogState {
  const CatalogState({
    this.items = const [],
    this.isLoading = false,
    this.error,
    this.page = 0,
    this.totalPages = 1,
    this.total = 0,
    this.filter = const CatalogFilter(),
    this.categories = const [],
    this.branches = const [],
  });

  final List<Product> items;
  final bool isLoading;
  final String? error;
  final int page;
  final int totalPages;
  final int total;
  final CatalogFilter filter;
  final List<Category> categories;

  /// CU-14: sucursales disponibles para filtrar por disponibilidad.
  final List<Branch> branches;

  CatalogState copyWith({
    List<Product>? items,
    bool? isLoading,
    String? error,
    int? page,
    int? totalPages,
    int? total,
    CatalogFilter? filter,
    List<Category>? categories,
    List<Branch>? branches,
  }) {
    return CatalogState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      page: page ?? this.page,
      totalPages: totalPages ?? this.totalPages,
      total: total ?? this.total,
      filter: filter ?? this.filter,
      categories: categories ?? this.categories,
      branches: branches ?? this.branches,
    );
  }
}

class CatalogController extends StateNotifier<CatalogState> {
  CatalogController(this._api) : super(const CatalogState()) {
    _loadCategories();
    loadBranches();
  }

  final ApiClient _api;

  /// CU-14: sucursar con existencia para consultar disponibilidad.
  Future<void> loadBranches() async {
    try {
      final list = await _api.getList('/locations/branches');
      state = state.copyWith(
        branches: list
            .map((e) => Branch.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
    } catch (_) {
      // El filtro por sucursal es opcional; el catalogo sigue funcionando.
    }
  }

  /// CU-14: disponibilidad por sucursal de una prenda.
  Future<List<VariantAvailability>> availability(int garmentId) async {
    final list = await _api.getList('/catalog/$garmentId/availability');
    return list
        .map((e) => VariantAvailability.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> _loadCategories() async {
    try {
      final res = await _api.get('/catalog/categories');
      final categories = (res['items'] as List? ?? const [])
          .map((e) => Category.fromJson(e as Map<String, dynamic>))
          .toList();
      state = state.copyWith(categories: categories);
    } catch (_) {
      // Categories are optional; catalog still loads.
    }
  }

  /// CU-13/CU-14: parametros de consulta derivados del filtro activo.
  Map<String, dynamic> _queryFor(int page) {
    final f = state.filter;
    return {
      'page': page,
      'size': 24,
      if (f.search.isNotEmpty) 'search': f.search,
      if (f.categoryId != null) 'category_id': f.categoryId,
      if (f.branchId != null) 'branch_id': f.branchId,
      if (f.minPrice != null) 'min_price': f.minPrice,
      if (f.maxPrice != null) 'max_price': f.maxPrice,
      if (f.sizes.isNotEmpty) 'sizes': f.sizes.toList(),
      if (f.colors.isNotEmpty) 'colors': f.colors.toList(),
      if (f.inStockOnly) 'in_stock': true,
      if (f.sortBy != null) 'sort_by': f.sortBy,
    };
  }

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, error: null, page: 0);
    try {
      final res = await _api.get('/catalog', queryParameters: _queryFor(1));
      final pageData = CatalogPage.fromJson(_asPage(res));
      state = state.copyWith(
        items: pageData.items,
        total: pageData.total,
        totalPages: pageData.totalPages,
        page: pageData.page,
        isLoading: false,
      );
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    }
  }

  Future<void> loadNextPage() async {
    if (state.isLoading || state.page + 1 >= state.totalPages) return;
    state = state.copyWith(isLoading: true);
    try {
      final res = await _api.get(
        '/catalog',
        queryParameters: _queryFor(state.page + 2), // backend 1-based
      );
      final pageData = CatalogPage.fromJson(_asPage(res));
      state = state.copyWith(
        items: [...state.items, ...pageData.items],
        page: pageData.page,
        total: pageData.total,
        totalPages: pageData.totalPages,
        isLoading: false,
      );
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    }
  }

  Future<void> applyFilter(CatalogFilter filter) async {
    state = state.copyWith(filter: filter);
    await loadFirstPage();
  }

  /// CU-14: filtra el catalogo por la disponibilidad en una sucursal.
  Future<void> selectBranch(int? branchId) async {
    state = state.copyWith(filter: state.filter.withBranch(branchId));
    await loadFirstPage();
  }

  Future<void> clearFilters() async {
    state = state.copyWith(filter: const CatalogFilter());
    await loadFirstPage();
  }

  /// Handles server response shapes: { items, ... } or bare list.
  Map<String, dynamic> _asPage(Map<String, dynamic> res) {
    return res;
  }

  Future<Product> getProduct(int id) async {
    final res = await _api.get('/catalog/$id');
    return Product.fromJson(res['product'] as Map<String, dynamic>? ?? res);
  }
}

final catalogControllerProvider =
    StateNotifierProvider<CatalogController, CatalogState>((ref) {
  return CatalogController(ref.watch(apiClientProvider));
});

final catalogFilterProvider =
    StateProvider<CatalogFilter>((ref) => const CatalogFilter());