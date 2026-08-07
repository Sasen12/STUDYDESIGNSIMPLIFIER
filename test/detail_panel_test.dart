import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:vce_unpacked/models/study_item.dart';
import 'package:vce_unpacked/theme/app_colors.dart';
import 'package:vce_unpacked/widgets/detail_panel.dart';

StudyItem _item({bool isCompleted = false}) {
  return StudyItem(
    id: 'sd-outcome-1',
    subject: 'Physics',
    title: 'Outcome 1',
    category: 'Outcome',
    officialText: 'Investigate waves and their properties.',
    plainLanguageText: 'Study how waves behave in different situations.',
    unit: 'Unit 1',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
    isCompleted: isCompleted,
  );
}

Widget _wrap(Widget child) {
  return MaterialApp(
    theme: ThemeData.light().copyWith(extensions: [AppColors.light]),
    home: Scaffold(body: child),
  );
}

void main() {
  testWidgets('shows the empty state when no item is selected',
      (tester) async {
    await tester.pumpWidget(
      _wrap(DetailPanel(item: null, onCompletionChanged: (_) {})),
    );

    expect(
      find.text('Select a study item to view details'),
      findsOneWidget,
    );
  });

  testWidgets('toggling completion reports the new value', (tester) async {
    bool? reported;
    await tester.pumpWidget(
      _wrap(
        DetailPanel(
          item: _item(),
          onCompletionChanged: (value) => reported = value,
        ),
      ),
    );
    await tester.pump(const Duration(milliseconds: 250)); // let switchers settle

    await tester.tap(find.text('Mark Complete'));
    await tester.pump();
    expect(reported, isTrue);
  });

  testWidgets('a completed item offers to mark it incomplete', (tester) async {
    bool? reported;
    await tester.pumpWidget(
      _wrap(
        DetailPanel(
          item: _item(isCompleted: true),
          onCompletionChanged: (value) => reported = value,
        ),
      ),
    );
    await tester.pump(const Duration(milliseconds: 250));

    await tester.tap(find.text('Mark Incomplete'));
    await tester.pump();
    expect(reported, isFalse);
  });
}
