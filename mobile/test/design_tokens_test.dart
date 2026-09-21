import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:fashionstore_mobile/core/design/design.dart';

void main() {
  group('Design tokens', () {
    test('primary uses the approved #FF8C00 palette', () {
      expect(AppColors.primary, const Color(0xFFFF8C00));
      expect(AppColors.primaryHover, const Color(0xFFE67E00));
      expect(AppColors.primaryLight, const Color(0xFFFFF3E0));
      expect(AppColors.primaryDark, const Color(0xFFCC7000));
    });

    test('semantic colors are defined', () {
      expect(AppColors.success, const Color(0xFF059669));
      expect(AppColors.warning, const Color(0xFFD97706));
      expect(AppColors.error, const Color(0xFFDC2626));
      expect(AppColors.info, const Color(0xFF0284C7));
    });

    test('light theme primary maps to palette', () {
      expect(AppColorScheme.light.primary, AppColors.primary);
    });
  });
}