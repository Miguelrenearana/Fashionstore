import 'package:flutter/material.dart';

import '../../../core/design/design.dart';
import '../../../core/models/catalog.dart';
import '../../../shared/widgets/shared_widgets.dart';
import '../catalog_controller.dart';

class FilterSheet extends StatefulWidget {
  const FilterSheet({
    super.key,
    required this.filter,
    required this.categories,
    required this.onApply,
  });

  final CatalogFilter filter;
  final List<Category> categories;
  final Future<void> Function(CatalogFilter) onApply;

  @override
  State<FilterSheet> createState() => _FilterSheetState();
}

class _FilterSheetState extends State<FilterSheet> {
  late String? _categoryId;
  late bool _inStockOnly;
  late String? _sortBy;
  final _sizes = <String>{};
  final _colors = <String>{};

  static const _allSizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];
  static const _allColors = ['Rojo', 'Azul', 'Verde', 'Negro', 'Blanco', 'Gris'];

  @override
  void initState() {
    super.initState();
    _categoryId = widget.filter.categoryId?.toString();
    _inStockOnly = widget.filter.inStockOnly;
    _sortBy = widget.filter.sortBy;
    _sizes.addAll(widget.filter.sizes);
    _colors.addAll(widget.filter.colors);
  }

  void _apply() {
    final filter = widget.filter.copyWith(
      categoryId: _categoryId != null ? int.tryParse(_categoryId!) : null,
      sizes: _sizes,
      colors: _colors,
      inStockOnly: _inStockOnly,
      sortBy: _sortBy,
    );
    widget.onApply(filter);
    Navigator.pop(context);
  }

  void _clear() {
    setState(() {
      _categoryId = null;
      _inStockOnly = false;
      _sortBy = null;
      _sizes.clear();
      _colors.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final size = MediaQuery.of(context).size;

    return Container(
      height: size.height * 0.85,
      decoration: const BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(AppRadius.lg),
        ),
      ),
      child: Column(
        children: [
          const DragHandle(),
          Padding(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.x5,
              AppSpacing.x2,
              AppSpacing.x5,
              AppSpacing.x2,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Filtros', style: theme.textTheme.headlineSmall),
                TextButton.icon(
                  onPressed: _clear,
                  icon: const Icon(Icons.filter_alt_off_outlined, size: 18),
                  label: const Text('Limpiar todos'),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: AppColors.border),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(AppSpacing.x5),
              children: [
                const _SectionTitle('Ordenar'),
                const SizedBox(height: AppSpacing.x2),
                Wrap(
                  spacing: AppSpacing.x2,
                  runSpacing: AppSpacing.x2,
                  children: [
                    for (final (value, label) in const [
                      ('price_asc', 'Precio menor'),
                      ('price_desc', 'Precio mayor'),
                      ('newest', 'Novedades'),
                      ('popular', 'Populares'),
                      ('rating', 'Mejor valorados'),
                    ])
                      ChoiceChip(
                        label: Text(label),
                        selected: _sortBy == value,
                        onSelected: (_) => setState(() => _sortBy = value),
                      ),
                  ],
                ),
                const SizedBox(height: AppSpacing.x5),
                const _SectionTitle('Categorías'),
                const SizedBox(height: AppSpacing.x2),
                Wrap(
                  spacing: AppSpacing.x2,
                  runSpacing: AppSpacing.x2,
                  children: [
                    ChoiceChip(
                      label: const Text('Todas'),
                      selected: _categoryId == null,
                      onSelected: (_) => setState(() => _categoryId = null),
                    ),
                    for (final c in widget.categories)
                      ChoiceChip(
                        label: Text(c.name),
                        selected: _categoryId == c.id.toString(),
                        onSelected: (_) =>
                            setState(() => _categoryId = c.id.toString()),
                      ),
                  ],
                ),
                const SizedBox(height: AppSpacing.x5),
                const _SectionTitle('Tallas'),
                const SizedBox(height: AppSpacing.x2),
                AppChipSelector(
                  items: _allSizes,
                  selected: _sizes,
                  onChanged: (v) => setState(() => _sizes
                    ..clear()
                    ..addAll(v)),
                  multiSelect: true,
                ),
                const SizedBox(height: AppSpacing.x5),
                const _SectionTitle('Colores'),
                const SizedBox(height: AppSpacing.x2),
                AppChipSelector(
                  items: _allColors,
                  selected: _colors,
                  onChanged: (v) => setState(() => _colors
                    ..clear()
                    ..addAll(v)),
                  multiSelect: true,
                ),
                const SizedBox(height: AppSpacing.x5),
                const _SectionTitle('Disponibilidad'),
                SwitchListTile(
                  value: _inStockOnly,
                  onChanged: (v) => setState(() => _inStockOnly = v),
                  title: const Text('Solo en stock'),
                  subtitle: const Text(
                    'Mostrar solo prendas disponibles',
                    style: TextStyle(fontSize: 13),
                  ),
                  contentPadding: EdgeInsets.zero,
                ),
                const SizedBox(height: AppSpacing.x6),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(AppSpacing.x4),
            child: AppButton(
              label: 'Aplicar filtros',
              size: AppButtonSize.lg,
              icon: Icons.filter_alt,
              onPressed: _apply,
            ),
          ),
          const SizedBox(height: AppSpacing.x2),
        ],
      ),
    );
  }
}

class DragHandle extends StatelessWidget {
  const DragHandle({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: AppSpacing.x3),
      width: 40,
      height: 4,
      decoration: BoxDecoration(
        color: AppColors.border,
        borderRadius: BorderRadius.circular(AppRadius.full),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.title);

  final String title;

  @override
  Widget build(BuildContext context) {
    return Text(
      title.toUpperCase(),
      style: Theme.of(context).textTheme.labelSmall?.copyWith(
            color: AppColors.textMuted,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.5,
          ),
    );
  }
}