import 'package:flutter/material.dart';

import '../../core/design/design.dart';
import 'app_empty_state.dart';

class AppDataColumn<T> {
  const AppDataColumn({
    required this.header,
    required this.cellBuilder,
    this.flex = 1,
    this.sortable = false,
    this.alignment = Alignment.centerLeft,
  });

  final String header;
  final Widget Function(BuildContext, T) cellBuilder;
  final int flex;
  final bool sortable;
  final Alignment alignment;
}

class AppDataTable<T> extends StatelessWidget {
  const AppDataTable({
    super.key,
    required this.columns,
    required this.items,
    this.filteredHeight,
    this.sortBy,
    this.onSort,
    this.emptyMessage = 'Sin resultados',
    this.emptyIcon = Icons.table_rows_outlined,
  });

  final List<AppDataColumn<T>> columns;
  final List<T> items;
  final double? filteredHeight;
  final String? sortBy;
  final ValueChanged<String?>? onSort;
  final String emptyMessage;
  final IconData emptyIcon;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (items.isEmpty) {
      return SizedBox(
        height: filteredHeight,
        child: AppEmptyState(
          title: emptyMessage,
          icon: emptyIcon,
        ),
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final isMobile = constraints.maxWidth < AppBreakpoints.sm;
        if (isMobile) return _mobileList(context, theme);
        return _desktopTable(context, theme);
      },
    );
  }

  Widget _desktopTable(BuildContext context, ThemeData theme) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingRowColor: WidgetStatePropertyAll(
          theme.brightness == Brightness.dark
              ? AppColors.darkSurfaceAlt
              : AppColors.surfaceAlt,
        ),
        dataRowMinHeight: 52,
        dataRowMaxHeight: 68,
        headingTextStyle: theme.textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.w700,
          color: AppColors.textSecondary,
        ),
        dataTextStyle: theme.textTheme.bodyMedium,
        dividerThickness: 1,
        columnSpacing: AppSpacing.x6,
        horizontalMargin: AppSpacing.x5,
        headingRowHeight: 48,
        sortColumnIndex: columns.indexWhere((c) => c.header.compareTo(sortBy ?? '') == 0) == -1 ? null : columns.indexWhere((c) => c.header == sortBy),
        sortAscending: true,
        columns: [
          for (final col in columns)
            DataColumn(
              label: Text(
                col.header,
                style: theme.textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.textSecondary,
                ),
              ),
              numeric: col.alignment == Alignment.centerRight,
              onSort: col.sortable && onSort != null
                  ? (_, __) => onSort!(col.header)
                  : null,
            ),
        ],
        rows: [
          for (final item in items)
            DataRow(
              cells: [
                for (final col in columns)
                  DataCell(
                    Container(
                      alignment: col.alignment == Alignment.centerRight
                          ? Alignment.centerRight
                          : Alignment.centerLeft,
                      margin: const EdgeInsets.symmetric(vertical: AppSpacing.x2),
                      child: col.cellBuilder(context, item),
                    ),
                  ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _mobileList(BuildContext context, ThemeData theme) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        final first = columns.first;
        return Container(
          margin: const EdgeInsets.symmetric(
            horizontal: AppSpacing.x4,
            vertical: AppSpacing.x2,
          ),
          padding: const EdgeInsets.all(AppSpacing.x4),
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            borderRadius: BorderRadius.circular(AppRadius.lg),
            border: Border.all(
              color: theme.brightness == Brightness.dark
                  ? AppColors.darkBorder
                  : AppColors.border,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              first.cellBuilder(context, item),
              const SizedBox(height: AppSpacing.x3),
              for (final col in columns.skip(1))
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 110,
                        child: Text(
                          col.header,
                          style: theme.textTheme.labelSmall
                              ?.copyWith(color: AppColors.textMuted),
                        ),
                      ),
                      Expanded(child: col.cellBuilder(context, item)),
                    ],
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}

class AppDataTablePagination extends StatelessWidget {
  const AppDataTablePagination({
    super.key,
    required this.page,
    required this.totalPages,
    required this.onPageChanged,
  });

  final int page;
  final int totalPages;
  final ValueChanged<int> onPageChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          onPressed: page > 0 ? () => onPageChanged(page - 1) : null,
          icon: const Icon(Icons.chevron_left),
          tooltip: 'Anterior',
        ),
        Text(
          'Página ${page + 1} de $totalPages',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        IconButton(
          onPressed: page < totalPages - 1 ? () => onPageChanged(page + 1) : null,
          icon: const Icon(Icons.chevron_right),
          tooltip: 'Siguiente',
        ),
      ],
    );
  }
}