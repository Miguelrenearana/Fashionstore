import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/design/design.dart';
import '../../core/di/providers.dart';
import '../../core/models/catalog.dart';
import '../../shared/widgets/shared_widgets.dart';
import '../reservations/reservation_controller.dart';
import 'catalog_controller.dart';

class ProductDetailScreen extends ConsumerStatefulWidget {
  const ProductDetailScreen({super.key, required this.productId});

  final int productId;

  @override
  ConsumerState<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends ConsumerState<ProductDetailScreen> {
  Product? _product;
  String? _error;
  bool _loading = true;
  int _imageIndex = 0;
  String? _selectedSize;
  String? _selectedColor;
  int _quantity = 1;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final product = await ref
          .read(catalogControllerProvider.notifier)
          .getProduct(widget.productId);
      if (!mounted) return;
      setState(() {
        _product = product;
        _loading = false;
        if (product.variants.isNotEmpty) {
          _selectedSize ??= product.variants.first.size.name;
          _selectedColor ??= product.variants.first.color.name;
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Detalle')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    final product = _product;
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(),
      body: product == null
          ? AppEmptyState(
              title: 'No se pudo cargar el producto',
              message: _error,
              icon: Icons.error_outline,
              actionLabel: 'Reintentar',
              onAction: _load,
            )
          : _buildContent(product),
    );
  }

  Widget _buildContent(Product product) {
    return Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _Gallery(
                  images: product.images,
                  initialIndex: _imageIndex,
                  onIndexChanged: (i) => _imageIndex = i,
                ),
                Padding(
                  padding: const EdgeInsets.all(AppSpacing.x5),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          if (product.brand != null)
                            Text(
                              product.brand!.toUpperCase(),
                              style: Theme.of(context)
                                  .textTheme
                                  .labelSmall
                                  ?.copyWith(
                                    color: AppColors.textMuted,
                                    letterSpacing: 1,
                                  ),
                            ),
                          const Spacer(),
                          if (product.rating > 0)
                            Row(
                              children: [
                                const Icon(
                                  Icons.star,
                                  size: 16,
                                  color: AppColors.warning,
                                ),
                                const SizedBox(width: 2),
                                Text(
                                  '${product.rating.toStringAsFixed(1)} · ${product.reviewCount}',
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodySmall
                                      ?.copyWith(
                                        color: AppColors.textSecondary,
                                      ),
                                ),
                              ],
                            ),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.x2),
                      Text(
                        product.name,
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: AppSpacing.x2),
                      CurrentPriceText(product: product, large: true),
                      const SizedBox(height: AppSpacing.x4),
                      if (product.variants.isNotEmpty) ...[
                        AppChipSelector(
                          label: 'Talla',
                          items: product.variants
                              .map((v) => v.size.name)
                              .toSet()
                              .toList(),
                          selected: {_selectedSize ?? ''},
                          onChanged: (v) => setState(() {
                            _selectedSize =
                                v.isNotEmpty ? v.first : _selectedSize;
                          }),
                        ),
                        const SizedBox(height: AppSpacing.x4),
                        AppChipSelector(
                          label: 'Color',
                          items: product.variants
                              .map((v) => v.color.name)
                              .toSet()
                              .toList(),
                          selected: {_selectedColor ?? ''},
                          onChanged: (v) => setState(() {
                            _selectedColor =
                                v.isNotEmpty ? v.first : _selectedColor;
                          }),
                        ),
                        const SizedBox(height: AppSpacing.x5),
                      ],
                      _QuantityStepper(
                        quantity: _quantity,
                        onChanged: (v) => setState(() => _quantity = v),
                      ),
                      const SizedBox(height: AppSpacing.x3),
                      _AvailabilityTile(product: product),
                      const SizedBox(height: AppSpacing.x4),
                      Text(
                        'Descripción',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: AppSpacing.x2),
                      Text(
                        product.description ?? 'Sin descripción disponible.',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AppColors.textSecondary,
                              height: 1.6,
                            ),
                      ),
                      const SizedBox(height: AppSpacing.x5),
                      Text(
                        'Características',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: AppSpacing.x2),
                      for (final tag in product.tags)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 2),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.check_circle_outline,
                                size: 16,
                                color: AppColors.success,
                              ),
                              const SizedBox(width: 8),
                              Text(tag),
                            ],
                          ),
                        ),
                      const SizedBox(height: AppSpacing.x5),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        SafeArea(
          top: false,
          child: Container(
            padding: const EdgeInsets.all(AppSpacing.x4),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              boxShadow: AppShadows.lg,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(AppRadius.lg),
              ),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: AppButton(
                        label: 'Reservar',
                        variant: AppButtonVariant.secondary,
                        icon: Icons.event_available_outlined,
                        onPressed: _showReserveSheet,
                      ),
                    ),
                    const SizedBox(width: AppSpacing.x3),
                    Expanded(
                      child: AppButton(
                        label: 'Agregar al carrito',
                        variant: AppButtonVariant.secondary,
                        icon: Icons.add_shopping_cart,
                        onPressed: () {
                          AppToast.show(
                            context,
                            message: 'Agregado al carrito',
                            type: ToastType.success,
                          );
                          context.go('/cart');
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.x3),
                AppButton(
                  label: 'Probar en AR',
                  icon: Icons.auto_awesome,
                  onPressed: () {
                    final variant = product.variants.isEmpty
                        ? null
                        : product.variants.firstWhere(
                            (v) =>
                                v.size.name ==
                                    (_selectedSize ?? product.variants.first.size.name) &&
                                v.color.name ==
                                    (_selectedColor ?? product.variants.first.color.name),
                            orElse: () => product.variants.first,
                          );
                    context.go('/fitting/${variant?.id ?? product.id}');
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _showReserveSheet() async {
    final product = _product;
    if (product == null || product.variants.isEmpty) return;
    final variant = product.variants.firstWhere(
      (v) =>
          v.size.name ==
              (_selectedSize ?? product.variants.first.size.name) &&
          v.color.name ==
              (_selectedColor ?? product.variants.first.color.name),
      orElse: () => product.variants.first,
    );

    final branchFuture = ref.read(apiClientProvider).get('/locations/branches');
    final branchesData = await branchFuture;
    final branches = (branchesData['items'] as List? ?? branchesData as List?)
            ?.map((e) => {
                  'id': e['id'] as int,
                  'name': e['name'] as String? ?? 'Sucursal',
                })
            .toList() ??
        const [];

    if (!mounted || branches.isEmpty) return;

    int? selectedBranchId = branches.first['id'] as int;
    int reserveQuantity = 1;

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
          ),
          child: Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(AppRadius.lg)),
            ),
            padding: const EdgeInsets.all(AppSpacing.x5),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Reservar en tienda',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.x3),
                Text(
                  '${product.name} — ${variant.size.name} / ${variant.color.name}',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: AppSpacing.x4),
                Text('Sucursal', style: Theme.of(context).textTheme.labelLarge),
                const SizedBox(height: AppSpacing.x2),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.x3),
                  decoration: BoxDecoration(
                    border: Border.all(color: AppColors.border),
                    borderRadius: BorderRadius.circular(AppRadius.lg),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<int>(
                      isExpanded: true,
                      value: selectedBranchId,
                      items: branches
                          .map((b) => DropdownMenuItem<int>(
                                value: b['id'] as int,
                                child: Text(b['name'] as String),
                              ))
                          .toList(),
                      onChanged: (v) => setSheetState(() => selectedBranchId = v),
                    ),
                  ),
                ),
                const SizedBox(height: AppSpacing.x4),
                _QuantityStepper(
                  quantity: reserveQuantity,
                  onChanged: (v) => setSheetState(() => reserveQuantity = v),
                ),
                const SizedBox(height: AppSpacing.x5),
                SizedBox(
                  width: double.infinity,
                  child: AppButton(
                    label: 'Confirmar reserva',
                    icon: Icons.check_circle_outline,
                    onPressed: () async {
                      Navigator.pop(context);
                      try {
                        await ref
                            .read(reservationControllerProvider.notifier)
                            .create(
                              items: [
                                {'variant_id': variant.id, 'quantity': reserveQuantity}
                              ],
                              branchId: selectedBranchId,
                            );
                        if (mounted) {
                          AppToast.show(context,
                              message: 'Reserva creada', type: ToastType.success);
                          context.go('/reservations');
                        }
                      } catch (e) {
                        if (mounted) {
                          AppToast.show(context,
                              message: 'Error: ${e.toString()}', type: ToastType.error);
                        }
                      }
                    },
                  ),
                ),
                const SizedBox(height: AppSpacing.x3),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Gallery extends StatefulWidget {
  const _Gallery({
    required this.images,
    required this.initialIndex,
    required this.onIndexChanged,
  });

  final List<String> images;
  final int initialIndex;
  final ValueChanged<int> onIndexChanged;

  @override
  State<_Gallery> createState() => _GalleryState();
}

class _GalleryState extends State<_Gallery> {
  late PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(initialPage: widget.initialIndex);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final images = widget.images.isNotEmpty
        ? widget.images
        : const <String>[];

    return Stack(
      children: [
        AspectRatio(
          aspectRatio: 1,
          child: images.isEmpty
              ? const _GalleryFallback()
              : PageView.builder(
                  controller: _pageController,
                  onPageChanged: widget.onIndexChanged,
                  itemCount: images.length,
                  itemBuilder: (context, i) => CachedNetworkImage(
                    imageUrl: images[i],
                    fit: BoxFit.cover,
                    placeholder: (_, __) => const AppSkeleton(
                      width: double.infinity,
                      height: double.infinity,
                    ),
                    errorWidget: (_, __, ___) => const _GalleryFallback(),
                  ),
                ),
        ),
        if (images.length > 1)
          Positioned(
            bottom: AppSpacing.x3,
            right: AppSpacing.x3,
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.x3,
                vertical: AppSpacing.x1,
              ),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.6),
                borderRadius: BorderRadius.circular(AppRadius.full),
              ),
              child: Text(
                '${widget.initialIndex + 1}/${images.length}',
                style: const TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
          ),
      ],
    );
  }
}

class _GalleryFallback extends StatelessWidget {
  const _GalleryFallback();

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.surfaceAlt,
      child: const Center(
        child: Icon(
          Icons.checkroom,
          size: 96,
          color: AppColors.textMuted,
        ),
      ),
    );
  }
}

class _QuantityStepper extends StatelessWidget {
  const _QuantityStepper({required this.quantity, required this.onChanged});

  final int quantity;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text('Cantidad', style: Theme.of(context).textTheme.labelLarge),
        const Spacer(),
        IconButton.filledTonal(
          onPressed: quantity > 1 ? () => onChanged(quantity - 1) : null,
          icon: const Icon(Icons.remove),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.x4),
          child: Text(
            '$quantity',
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
        ),
        IconButton.filledTonal(
          onPressed: quantity < 99 ? () => onChanged(quantity + 1) : null,
          icon: const Icon(Icons.add),
        ),
      ],
    );
  }
}

class _AvailabilityTile extends StatelessWidget {
  const _AvailabilityTile({required this.product});

  final Product product;

  @override
  Widget build(BuildContext context) {
    final inStock = product.variants.any((v) => v.inStock);
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(
        inStock ? Icons.inventory_2_outlined : Icons.inventory_2_outlined,
        color: inStock ? AppColors.success : AppColors.error,
      ),
      title: Text(
        inStock ? 'Disponible en tienda' : 'Agotado temporalmente',
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
      ),
      subtitle: Text(
        inStock
            ? 'Consulta disponibilidad por sucursal o recógelo en la tienda más cercana'
            : 'Te notificaremos cuando esté disponible',
        style: Theme.of(context).textTheme.bodySmall,
      ),
    );
  }
}