import 'package:flutter_test/flutter_test.dart';
import 'package:vce_study_tracker/logic/study_filter.dart';
import 'package:vce_study_tracker/models/study_item.dart';

StudyItem _item({
  required String id,
  required String subject,
  required String category,
  String title = '',
  String officialText = '',
  String plainLanguageText = '',
}) {
  return StudyItem(
    id: id,
    subject: subject,
    title: title,
    category: category,
    officialText: officialText,
    plainLanguageText: plainLanguageText,
  );
}

void main() {
  final items = [
    _item(
      id: '1',
      subject: 'Physics',
      category: 'Outcome',
      title: 'Outcome 1',
      officialText: 'Investigate waves',
      plainLanguageText: 'Study how waves behave',
    ),
    _item(
      id: '2',
      subject: 'Physics',
      category: 'Key Knowledge',
      title: 'Characteristics of light',
      officialText: 'The characteristics of light',
      plainLanguageText: 'The traits of light',
    ),
    _item(
      id: '3',
      subject: 'General Mathematics',
      category: 'Key Skill',
      title: 'Solve equations',
      officialText: 'Solve linear equations',
      plainLanguageText: 'Work out equations',
    ),
    _item(
      id: '4',
      subject: 'Physics',
      category: 'Command Term',
      title: 'Analyse',
      officialText: 'Analyse',
      plainLanguageText: 'Break down and examine',
    ),
  ];

  List<String> ids(Iterable<StudyItem> result) =>
      result.map((i) => i.id).toList();

  test('no filters returns every item in original order', () {
    expect(ids(filterItems(items)), ['1', '2', '3', '4']);
  });

  test('subject filter narrows to one subject', () {
    expect(ids(filterItems(items, subject: 'Physics')), ['1', '2', '4']);
  });

  test("category 'All' is a no-op", () {
    expect(filterItems(items, category: 'All'), hasLength(items.length));
  });

  test('category filter narrows to one category', () {
    expect(ids(filterItems(items, category: 'Key Knowledge')), ['2']);
  });

  test('search matches title case-insensitively', () {
    expect(ids(filterItems(items, query: 'OUTCOME')), ['1']);
  });

  test('search matches official text', () {
    expect(ids(filterItems(items, query: 'linear')), ['3']);
  });

  test('search matches plain language text', () {
    expect(ids(filterItems(items, query: 'traits')), ['2']);
  });

  test('empty query returns every item', () {
    expect(filterItems(items, query: ''), hasLength(items.length));
  });

  test('all three axes are ANDed together', () {
    expect(
      ids(
        filterItems(
          items,
          subject: 'Physics',
          category: 'Outcome',
          query: 'waves',
        ),
      ),
      ['1'],
    );
  });

  test('no match yields an empty list', () {
    expect(filterItems(items, query: 'zzzznope'), isEmpty);
  });
}
