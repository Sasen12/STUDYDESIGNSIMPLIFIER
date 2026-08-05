import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:vce_study_tracker/models/study_item.dart';
import 'package:vce_study_tracker/theme/app_colors.dart';
import 'package:vce_study_tracker/widgets/results_list.dart';

StudyItem _item({
  required String id,
  required String category,
  String? unit,
  String? areaOfStudy,
  String title = '',
  String plainLanguageText = 'Some plain text',
}) {
  return StudyItem(
    id: id,
    subject: 'Physics',
    title: title.isEmpty ? 'Title $id' : title,
    category: category,
    officialText: 'Official $id',
    plainLanguageText: plainLanguageText,
    unit: unit,
    areaOfStudy: areaOfStudy,
  );
}

Widget _wrap(Widget child) {
  return MaterialApp(
    theme: ThemeData.light().copyWith(extensions: [AppColors.light]),
    home: Scaffold(body: child),
  );
}

void main() {
  testWidgets('groups items under Unit/Area headers with a trailing Glossary '
      'header', (tester) async {
    await tester.pumpWidget(
      _wrap(
        SizedBox(
          width: 400,
          height: 600,
          child: ResultsList(
            items: [
              _item(
                id: '1',
                category: 'Key Knowledge',
                unit: 'Unit 1',
                areaOfStudy: 'Area of Study 1',
                plainLanguageText: 'types of data, such as:; tables; queries',
              ),
              _item(id: '2', category: 'Command Term'), // no unit
              _item(id: '3', category: 'Command Term'), // no unit
            ],
            selectedItem: null,
            onItemSelected: (_) {},
            generation: 0,
            emptyMessage: 'None',
          ),
        ),
      ),
    );

    expect(find.text('Unit 1'), findsOneWidget);
    expect(find.text('Area of Study 1'), findsOneWidget);
    expect(find.text('Glossary of Command Terms'), findsOneWidget);
    // List-shaped content leads with its short headline, not the whole
    // joined list.
    expect(find.text('types of data, such as:'), findsOneWidget);
    expect(find.text('Title 2'), findsOneWidget);
    expect(find.text('Title 3'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('shows the empty message when there are no items',
      (tester) async {
    await tester.pumpWidget(
      _wrap(
        ResultsList(
          items: [],
          selectedItem: null,
          onItemSelected: (_) {},
          generation: 1,
          emptyMessage: 'No matches for "zzz"',
        ),
      ),
    );

    expect(find.text('No matches for "zzz"'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('tapping a card reports the selected item', (tester) async {
    final item = _item(id: '7', category: 'Outcome', title: 'Outcome 1');
    StudyItem? tapped;
    await tester.pumpWidget(
      _wrap(
        SizedBox(
          width: 400,
          height: 600,
          child: ResultsList(
            items: [item],
            selectedItem: null,
            onItemSelected: (i) => tapped = i,
            generation: 0,
            emptyMessage: 'None',
          ),
        ),
      ),
    );

    await tester.tap(find.text('Outcome 1'));
    await tester.pump();
    expect(tapped?.id, '7');
  });
}
