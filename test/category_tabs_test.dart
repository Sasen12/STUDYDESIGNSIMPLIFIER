import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:vce_study_tracker/theme/app_colors.dart';
import 'package:vce_study_tracker/widgets/category_tabs.dart';

void main() {
  testWidgets('segmented control renders all categories without overflow/crash', (tester) async {
    const categories = ['All', 'Outcome', 'Key Knowledge', 'Key Skill', 'Command Term'];

    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData.light().copyWith(extensions: [AppColors.light]),
        home: Scaffold(
          body: SizedBox(
            width: 500,
            child: CategoryTabs(
              categories: categories,
              selectedCategory: 'Key Knowledge',
              onCategorySelected: (_) {},
            ),
          ),
        ),
      ),
    );
    await tester.pump(const Duration(milliseconds: 250)); // let AnimatedPositioned settle

    for (final c in categories) {
      expect(find.text(c), findsOneWidget);
    }
    expect(tester.takeException(), isNull);

    // Tap a different segment and confirm the callback + re-render works.
    String? tapped;
    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData.light().copyWith(extensions: [AppColors.light]),
        home: Scaffold(
          body: SizedBox(
            width: 500,
            child: CategoryTabs(
              categories: categories,
              selectedCategory: 'Key Knowledge',
              onCategorySelected: (c) => tapped = c,
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Command Term'));
    expect(tapped, 'Command Term');
    expect(tester.takeException(), isNull);
  });
}
