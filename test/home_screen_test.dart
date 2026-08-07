import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vce_unpacked/data/study_data_repository.dart';
import 'package:vce_unpacked/models/study_item.dart';
import 'package:vce_unpacked/screens/home_screen.dart';
import 'package:vce_unpacked/theme/app_colors.dart';
import 'package:vce_unpacked/theme/theme_model.dart';

class _FakeStudyDataRepository extends StudyDataRepository {
  final List<StudyItem> items;
  _FakeStudyDataRepository(this.items);

  @override
  Future<List<StudyItem>> loadItems() async => items;
}

List<StudyItem> _fixtureItems() {
  return [
    StudyItem(
      id: '1',
      subject: 'Physics',
      title: 'Outcome 1',
      category: 'Outcome',
      officialText: 'Investigate waves.',
      plainLanguageText: 'Study how waves behave.',
      unit: 'Unit 1',
      areaOfStudy: 'Area of Study 1',
      outcome: 'Outcome 1',
    ),
    StudyItem(
      id: '2',
      subject: 'Physics',
      title: 'Title 2',
      category: 'Key Knowledge',
      officialText: 'Characteristics of light.',
      plainLanguageText: 'The traits of light.',
      unit: 'Unit 1',
      areaOfStudy: 'Area of Study 1',
    ),
    StudyItem(
      id: '3',
      subject: 'General Mathematics',
      title: 'Solve equations',
      category: 'Key Skill',
      officialText: 'Solve linear equations.',
      plainLanguageText: 'Work out equations.',
      unit: 'Unit 1',
      areaOfStudy: 'Area of Study 1',
    ),
  ];
}

void main() {
  testWidgets('typing a non-matching query shows the search empty message',
      (tester) async {
    SharedPreferences.setMockInitialValues({});

    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData.light().copyWith(extensions: [AppColors.light]),
        home: HomeScreen(
          themeModel: ThemeModel(),
          repository: _FakeStudyDataRepository(_fixtureItems()),
        ),
      ),
    );
    // Let the (immediately-resolving) fake load finish and rebuild.
    await tester.pump();
    await tester.pump();

    await tester.enterText(find.byType(TextField), 'zzznope');
    // Search is debounced (200ms) — let it fire and rebuild.
    await tester.pump(const Duration(milliseconds: 250));
    await tester.pump();

    expect(find.text('No matches for “zzznope”'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
