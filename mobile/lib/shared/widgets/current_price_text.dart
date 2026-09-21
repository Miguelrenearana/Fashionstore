import 'package:flutter/material.dart';

import '../../../core/design/design.dart';
import '../../../core/models/catalog.dart';

class CurrentPriceText extends StatelessWidget {
  const CurrentPriceText({super.key, required this.product, this.large = false});

  final Product product;
  final bool large;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final price = _fmt(product.finalPrice);
    final original = _fmt(product.price);

    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.baseline,
      textBaseline: TextBaseline.alphabetic,
      children: [
        Text(
          price,
          style: theme.textTheme.titleMedium?.copyWith(
            color: AppColors.primaryDark,
            fontWeight: FontWeight.w700,
            fontSize: large ? 20 : null,
          ),
        ),
        if (product.hasDiscount) ...[
          const SizedBox(width: 6),
          Text(
            original,
            style: theme.textTheme.bodySmall?.copyWith(
              color: AppColors.textMuted,
              decoration: TextDecoration.lineThrough,
            ),
          ),
        ],
      ],
    );
  }

  String _fmt(double value) {
    final s = value.toStringAsFixed(2);
    return s.endsWith('.00') ? s.substring(0, s.length - 3) : s;
  }
}