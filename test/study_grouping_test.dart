import 'package:flutter_test/flutter_test.dart';
import 'package:vce_unpacked/logic/study_grouping.dart';
import 'package:vce_unpacked/models/study_item.dart';

StudyItem _item({
  required String id,
  String? unit,
  String? areaOfStudy,
  String plainLanguageText = 'Some plain text',
}) {
  return StudyItem(
    id: id,
    subject: 'Physics',
    title: 'Title $id',
    category: 'Key Knowledge',
    officialText: 'Official $id',
    plainLanguageText: plainLanguageText,
    unit: unit,
    areaOfStudy: areaOfStudy,
  );
}

List<String> _headerTexts(List<StudyRow> rows) =>
    rows.whereType<StudyHeaderRow>().map((r) => r.text).toList();

void main() {
  test('glossary entries group under one trailing Glossary header', () {
    final rows = buildRows([
      _item(id: '1', unit: 'Unit 1', areaOfStudy: 'Area of Study 1'),
      _item(id: '2', unit: null), // Command Term glossary entry
      _item(id: '3', unit: null),
    ]);

    expect(rows, [
      isA<StudyHeaderRow>()
          .having((r) => r.text, 'text', 'Unit 1')
          .having((r) => r.isSubHeader, 'isSubHeader', false),
      isA<StudyHeaderRow>()
          .having((r) => r.text, 'text', 'Area of Study 1')
          .having((r) => r.isSubHeader, 'isSubHeader', true),
      isA<StudyItemRow>(),
      isA<StudyHeaderRow>()
          .having((r) => r.text, 'text', 'Glossary of Command Terms'),
      isA<StudyItemRow>(),
      isA<StudyItemRow>(),
    ]);
  });

  test('unit + area headers emit once for consecutive same-scope items', () {
    final rows = buildRows([
      _item(id: '1', unit: 'Unit 1', areaOfStudy: 'Area of Study 1'),
      _item(id: '2', unit: 'Unit 1', areaOfStudy: 'Area of Study 1'),
    ]);

    expect(_headerTexts(rows), ['Unit 1', 'Area of Study 1']);
  });

  test('area header re-emits when the area changes within a unit', () {
    final rows = buildRows([
      _item(id: '1', unit: 'Unit 1', areaOfStudy: 'Area of Study 1'),
      _item(id: '2', unit: 'Unit 1', areaOfStudy: 'Area of Study 2'),
    ]);

    expect(
      _headerTexts(rows),
      ['Unit 1', 'Area of Study 1', 'Area of Study 2'],
    );
  });

  test('area header re-emits after a unit change (unit resets area)', () {
    final rows = buildRows([
      _item(id: '1', unit: 'Unit 1', areaOfStudy: 'Area of Study 1'),
      _item(id: '2', unit: 'Unit 2', areaOfStudy: 'Area of Study 1'),
    ]);

    expect(
      _headerTexts(rows),
      ['Unit 1', 'Area of Study 1', 'Unit 2', 'Area of Study 1'],
    );
  });

  test('items with a null area get no area header', () {
    final rows = buildRows([_item(id: '1', unit: 'Unit 1', areaOfStudy: null)]);
    expect(_headerTexts(rows), ['Unit 1']);
  });

  test('empty items produce no rows', () {
    expect(buildRows([]), isEmpty);
  });

  group('cardHeadline', () {
    test('list-shaped text returns the lead-in before the first semicolon',
        () {
      final item = _item(
        id: '1',
        plainLanguageText: 'types of data, such as:; interviews; surveys',
      );
      expect(cardHeadline(item), 'types of data, such as:');
    });

    test('non-list text returns the full text', () {
      final item = _item(id: '1', plainLanguageText: 'Study how waves behave');
      expect(cardHeadline(item), 'Study how waves behave');
    });

    test('a bare semicolon (no following space) is not a list split', () {
      final item = _item(id: '1', plainLanguageText: 'no list here;');
      expect(cardHeadline(item), 'no list here;');
    });
  });
}
