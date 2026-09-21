import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/catalog.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';

class CatalogFilter {
  const CatalogFilter({
    this.search = '',
    this.categoryId,
    this.minPrice,
    this.maxPrice,
    this.sizes = const {},
    this.colors = const {},
    this.inStockOnly = false,
    this.sortBy,
  });

  final String search;
  final int? categoryId;
  final double? minPrice;
  final double? maxPrice;
  final Set<String> sizes;
  final Set<String> colors;
  final bool inStockOnly;
  final String? sortBy;

  bool get hasActiveFilters =>
      search.isNotEmpty ||
      categoryId != null ||
      minPrice != null ||
      maxPrice != null ||
      sizes.isNotEmpty ||
      colors.isNotEmpty ||
      inStockOnly;

  CatalogFilter copyWith({
    String? search,
    int? categoryId,
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
      minPrice: minPrice ?? this.minPrice,
      maxPrice: maxPrice ?? this.maxPrice,
      sizes: sizes ?? this.sizes,
      colors: colors ?? this.colors,
      inStockOnly: inStockOnly ?? this.inStockOnly,
      sortBy: sortBy ?? this.sortBy,
    );
  }
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
  });

  final List<Product> items;
  final bool isLoading;
  final String? error;
  final int page;
  final int totalPages;
  final int total;
  final CatalogFilter filter;
  final List<Category> categories;

  CatalogState copyWith({
    List<Product>? items,
    bool? isLoading,
    String? error,
    int? page,
    int? totalPages,
    int? total,
    CatalogFilter? filter,
    List<Category>? categories,
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
    );
  }
}

class CatalogController extends StateNotifier<CatalogState> {
  CatalogController(this._api) : super(const CatalogState()) {
    _loadCategories();
  }

  final ApiClient _api;

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

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, error: null, page: 0);
    final f = state.filter;
    try {
      final res = await _api.get('/catalog', queryParameters: {
        'page': 0,
        'size': 24,
        if (f.search.isNotEmpty) 'search': f.search,
        if (f.categoryId != null) 'category_id': f.categoryId,
        if (f.minPrice != null) 'min_price': f.minPrice,
        if (f.maxPrice != null) 'max_price': f.maxPrice,
        if (f.sizes.isNotEmpty) 'sizes': f.sizes.join(','),
        if (f.colors.isNotEmpty) 'colors': f.colors.join(','),
        if (f.inStockOnly) 'in_stock': true,
        if (f.sortBy != null) 'sort_by': f.sortBy,
      });
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
      final res = await _api.get('/catalog', queryParameters: {
        'page': state.page + 1,
        'size': 24,
      });
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