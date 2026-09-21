import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:fashionstore_mobile/core/design/design.dart';

void main() {
  testWidgets('Light theme builds a scaffold with primary palette', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme,
        home: const Scaffold(body: SizedBox()),
      ),
    );
    await tester.pump();

    final context = tester.element(find.byType(Scaffold));
    final theme = Theme.of(context);
    expect(theme.colorScheme.primary, AppColors.primary);
  });

  test('AppTheme exposes light and dark themes', () {
    expect(AppTheme.lightTheme.colorScheme.primary, AppColors.primary);
    expect(AppTheme.darkTheme.brightness, Brightness.dark);
  });
}