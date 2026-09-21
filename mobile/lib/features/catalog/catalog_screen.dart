import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/design/design.dart';
import '../../shared/widgets/shared_widgets.dart';
import 'catalog_controller.dart';
import 'widgets/filter_sheet.dart';
import 'widgets/product_card.dart';

class CatalogScreen extends ConsumerStatefulWidget {
  const CatalogScreen({super.key});

  @override
  ConsumerState<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends ConsumerState<CatalogScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();
  bool _gridView = true;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    Future.microtask(
      () => ref.read(catalogControllerProvider.notifier).loadFirstPage(),
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 300) {
      ref.read(catalogControllerProvider.notifier).loadNextPage();
    }
  }

  Future<void> _search(String query) async {
    final current = ref.read(catalogControllerProvider).filter;
    final notifier = ref.read(catalogControllerProvider.notifier);
    await notifier.applyFilter(current.copyWith(search: query));
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(catalogControllerProvider);
    final notifier = ref.read(catalogControllerProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Row(
          children: [
            Icon(Icons.checkroom, color: AppColors.primary, size: 26),
            SizedBox(width: 8),
            Text(
              'FashionStore',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () => context.go('/cart'),
            icon: const Icon(Icons.shopping_cart_outlined),
            tooltip: 'Carrito',
          ),
          IconButton(
            onPressed: () => context.go('/profile'),
            icon: const Icon(Icons.person_outline),
            tooltip: 'Perfil',
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.x4,
              AppSpacing.x3,
              AppSpacing.x4,
              AppSpacing.x2,
            ),
            child: Row(
              children: [
                Expanded(
                  child: AppTextField(
                    controller: _searchController,
                    hintText: 'Buscar prendas, marcas…',
                    prefixIcon: Icons.search,
                    onSubmitted: _search,
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            onPressed: () {
                              _searchController.clear();
                              _search('');
                            },
                            icon: const Icon(Icons.close, size: 20),
                          )
                        : null,
                  ),
                ),
                const SizedBox(width: AppSpacing.x2),
                IconButton.filledTonal(
                  onPressed: () => _openFilters(context),
                  style: IconButton.styleFrom(
                    backgroundColor: state.filter.hasActiveFilters
                        ? AppColors.primary
                        : AppColors.surface,
                    foregroundColor: state.filter.hasActiveFilters
                        ? Colors.white
                        : AppColors.textSecondary,
                  ),
                  icon: Badge(
                    isLabelVisible: state.filter.hasActiveFilters,
                    child: const Icon(Icons.tune),
                  ),
                  tooltip: 'Filtros',
                ),
                const SizedBox(width: AppSpacing.x2),
                IconButton.filledTonal(
                  onPressed: () => setState(() => _gridView = !_gridView),
                  icon: Icon(
                    _gridView ? Icons.view_list_outlined : Icons.grid_view_outlined,
                  ),
                  tooltip: _gridView ? 'Vista lista' : 'Vista cuadrícula',
                ),
              ],
            ),
          ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: () => notifier.loadFirstPage(),
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 200),
                child: _buildBody(state),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(CatalogState state) {
    if (state.isLoading && state.items.isEmpty) {
      return const _CatalogGrid(
        isGrid: true,
        children: [
          AppSkeletonCard(),
          AppSkeletonCard(),
          AppSkeletonCard(),
          AppSkeletonCard(),
        ],
      );
    }

    if (state.error != null && state.items.isEmpty) {
      return AppEmptyState(
        title: 'No pudimos cargar el catálogo',
        message: state.error,
        icon: Icons.cloud_off_outlined,
        actionLabel: 'Reintentar',
        onAction: () => ref
            .read(catalogControllerProvider.notifier)
            .loadFirstPage(),
      );
    }

    if (state.items.isEmpty) {
      return const AppEmptyState(
        title: 'No se encontraron prendas',
        message: 'Prueba con otros filtros o términos de búsqueda.',
        icon: Icons.search_off_outlined,
      );
    }

    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification.metrics.pixels >=
            notification.metrics.maxScrollExtent - 300) {
          ref.read(catalogControllerProvider.notifier).loadNextPage();
        }
        return false;
      },
      child: ListView(
        controller: _scrollController,
        padding: const EdgeInsets.all(AppSpacing.x4),
        children: [
          _CatalogGrid(
            isGrid: _gridView,
            children: [
              for (final p in state.items) ProductCard(product: p),
            ],
          ),
          if (state.isLoading) const Padding(
            padding: EdgeInsets.all(AppSpacing.x5),
            child: Center(child: CircularProgressIndicator()),
          ),
          const SizedBox(height: AppSpacing.x5),
        ],
      ),
    );
  }

  Future<void> _openFilters(BuildContext context) {
    return showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => FilterSheet(
        filter: ref.read(catalogControllerProvider).filter,
        categories: ref.read(catalogControllerProvider).categories,
        onApply: (filter) async {
          await ref
              .read(catalogControllerProvider.notifier)
              .applyFilter(filter);
        },
      ),
    );
  }
}

class _CatalogGrid extends StatelessWidget {
  const _CatalogGrid({required this.isGrid, required this.children});

  final bool isGrid;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final columns = isGrid
        ? (width >= 1200 ? 5 : width >= 900 ? 4 : width >= 600 ? 3 : 2)
        : 1;

    return LayoutBuilder(
      builder: (context, constraints) {
        if (isGrid) {
          return GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: columns,
              crossAxisSpacing: AppSpacing.x4,
              mainAxisSpacing: AppSpacing.x4,
              childAspectRatio: 0.66,
            ),
            itemCount: children.length,
            itemBuilder: (_, i) => children[i],
          );
        }
        return Column(
          children: [
            for (final child in children)
              Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.x3),
                child: child,
              ),
          ],
        );
      },
    );
  }
}